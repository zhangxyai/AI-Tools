import argparse
import yaml
from openai import OpenAI
import json
from enum import Enum

class TestMode(Enum):
    ALL = "all"
    SIMPLE = "simple"
    STRUCT_OUTPUT = "struct_output"
    FUNCTION_CALL = "function_call"
    

# read config.yaml
def read_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def config_parser(config):
    base_url = config['base_url']
    api_key = config.get('api_key', 'empty')
    model = config['model']
    test_mode = TestMode(config.get("test_mode", "all"))
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print("\n---------------Test Info---------------")
    print(f"Model Name: {model}")
    print(f"Base URL: {base_url}")
    print("---------------------------------------\n")
    
    return client, model, test_mode



def test_simple(client, model):
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "9.7和9.12哪个大？"}
        ]
    )

    print("\nSingle Test Response:")
    print("---------------------------------------")
    print("Thinking:")
    print(response.choices[0].message.reasoning_content)
    print("Content:")
    print(response.choices[0].message.content)
    print("---------------------------------------\n")


def test_struct_output(client, model):
    
    json_schema = json.dumps(
        {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": "^[\\w]+$"},
                "population": {"type": "integer"},
            },
            "required": ["name", "population"],
        }
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "请帮我整理中国首都的信息"}
        ],
        temperature=0,
        max_tokens=128,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "foo",
                "schema": json.loads(json_schema)
            },
        },
    )

    print("\nStruct Output Test Response:")
    print("---------------------------------------")
    print(response.choices[0].message.content)
    print("---------------------------------------\n")


def test_funcation_call(client, model):
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city to find the weather for, e.g. 'San Francisco'",
                        },
                        "state": {
                            "type": "string",
                            "description": "the two-letter abbreviation for the state that the city is"
                            " in, e.g. 'CA' which would mean 'California'",
                        },
                        "unit": {
                            "type": "string",
                            "description": "The unit to fetch the temperature in",
                            "enum": ["celsius", "fahrenheit"],
                        },
                    },
                    "required": ["city", "state", "unit"],
                },
            },
        }
    ]
    
    messages =[
        {
            "role": "user",
            "content": "What's the weather like in Boston today? Output a reasoning before act, then use the tools to help you.",
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        top_p=0.95,
        max_tokens=1024,
        stream=False,  # Non-streaming
        tools=tools,
    )


    print("\nStruct Output Test Response:")
    print("---------------------------------------")
    print("First Response Context:")
    print(response.choices[0].message.content)
    print("\n\nTool Calls:")
    print(response.choices[0].message.tool_calls)
    
    def get_current_weather(city: str, state: str, unit: "str"):
        return (
            f"The weather in {city}, {state} is 85 degrees {unit}. It is "
            "partly cloudly, with highs in the 90's."
        )
    available_tools = {"get_current_weather": get_current_weather}

    messages.append(response.choices[0].message)
    print(messages)
    tool_call = messages[-1].tool_calls[0]
    tool_name = tool_call.function.name
    tool_to_call = available_tools[tool_name]
    result = tool_to_call(**(json.loads(tool_call.function.arguments)))
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result),
            "name": tool_name,
        }
    )
    
    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        top_p=0.95,
        stream=False,
        tools=tools,
    )
 
    print("\n\n\nFinal Response: ")
    print(final_response.choices[0].message.content)
    print("---------------------------------------\n")


if __name__ == "__main__":
    ## config 为输入参数
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
    args = parser.parse_args()
    config_path = args.config
    config = read_config(config_path)
    client, model, test_mode = config_parser(config)
    if test_mode == TestMode.SIMPLE:
        test_simple(client, model)
    elif test_mode == TestMode.STRUCT_OUTPUT:
        test_struct_output(client, model)
    elif test_mode == TestMode.FUNCTION_CALL:
        test_funcation_call(client, model)
    else:
        print("Test Simple:")
        test_simple(client, model)
        print("\n\n\n\n\nTest Struct Output:")
        test_struct_output(client, model)
        print("\n\n\n\n\nTest Funcation Call: ")
        test_funcation_call(client, model)