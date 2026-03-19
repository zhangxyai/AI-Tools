import argparse
import yaml
import csv
import os
import shutil
from enum import Enum
# evalscope
from evalscope.perf.main import run_perf_benchmark
from evalscope.perf.arguments import Arguments


class TestMode(Enum):
    PREFILL = "prefill"
    DECODE = "decode"
    REGULAR = "regular"


# read config.yaml
def read_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def config_parser(config):
    test_mode = TestMode(config.get("mode", "regular"))
    result_file = config.get("result_file", "result.csv")
    
    model_config = config["model_config"]
    model = model_config ["model"]
    
    result_file = model+"_"+test_mode.value+"_"+result_file
    
    perf_config = config["perf_config"]
    
    epoch = perf_config.get("epoch", 10)
    concurrency_list = perf_config["concurrency"]
    number_list = [concurrency * epoch for concurrency in concurrency_list]
    
    input_tokens = perf_config["input_tokens"]
    
    if test_mode == TestMode.DECODE:
        prefix_length = [input_token-8 for input_token in input_tokens]
    else:
        prefix_length = [0] * len(input_tokens)
        
    if test_mode == TestMode.PREFILL:
        output_tokens = [1]
    else:
        output_tokens = perf_config["output_tokens"]
    
    return test_mode, result_file, model_config, concurrency_list, number_list, input_tokens, prefix_length, output_tokens


def extract_result_metrics(results):
    """从evalscope结果中提取指标
    
    Args:
        results: evalscope返回的结果
            - 旧版本 (0.17.0): 元组 (metrics_dict, percentiles_dict)
            - 新版本: 字典 {'parallel_X_number_Y': {'metrics': {...}, 'percentiles': {...}}}
    
    Returns:
        包含所需指标的字典
    """
    # 兼容两种格式
    if isinstance(results, tuple):
        # 旧版本格式: (metrics, percentiles)
        metrics, percentiles = results
    elif isinstance(results, dict):
        # 新版本格式: {'parallel_X_number_Y': {'metrics': {...}, 'percentiles': {...}}}
        # 获取第一个键对应的值
        first_key = next(iter(results))
        metrics = results[first_key]['metrics']
        percentiles = results[first_key]['percentiles']
    else:
        raise ValueError(f"不支持的结果格式: {type(results)}")
    
    # 找到90%对应的索引
    percentile_labels = percentiles['Percentiles']
    p90_index = percentile_labels.index('90%')
    
    extracted = {
        'ttft': metrics['Average time to first token (s)'],
        'p90_ttft': percentiles['TTFT (s)'][p90_index],
        'tpot': metrics['Average time per output token (s)'],
        'p90_tpot': percentiles['TPOT (s)'][p90_index],
        'input_token_throughput': (
            metrics['Total token throughput (tok/s)'] - 
            metrics['Output token throughput (tok/s)']
        ),
        'output_token_throughput': metrics['Output token throughput (tok/s)'],
        'total_token_throughput': metrics['Total token throughput (tok/s)']
    }
    
    return extracted


def clean_outputs_folder(outputs_dir='outputs'):
    """清理evalscope生成的outputs文件夹
    
    Args:
        outputs_dir: outputs文件夹路径，默认为'outputs'
    """
    if os.path.exists(outputs_dir):
        try:
            shutil.rmtree(outputs_dir)
            print(f"  已清理 {outputs_dir} 文件夹")
        except Exception as e:
            print(f"  警告: 清理 {outputs_dir} 失败: {e}")


def get_fieldnames_by_mode(test_mode):
    """根据mode获取对应的CSV字段名
    
    Args:
        mode: 测试模式 ('all', 'prefill', 'decode')
    
    Returns:
        字段名列表
    """
    if test_mode == TestMode.PREFILL:
        return ['input_tokens', 'output_tokens', 'concurrency', 'number', 'ttft', 'p90_ttft', 'input_token_throughput']
    elif test_mode == TestMode.DECODE:
        return ['input_tokens', 'prefix_length', 'output_tokens', 'concurrency', 'number', 'tpot', 'p90_tpot', 'output_token_throughput']
    else:
        return ['input_tokens', 'output_tokens', 'concurrency', 'number','ttft', 'p90_ttft', 'tpot', 'p90_tpot','input_token_throughput', 'output_token_throughput', 'total_token_throughput']


def write_to_csv(output_file, test_params, metrics, is_new_file, mode=TestMode.REGULAR):
    """将测试结果写入CSV文件
    
    Args:
        output_file: 输出文件路径
        test_params: 测试参数字典
        metrics: 提取的指标字典
        is_new_file: 是否是新文件（需要写表头）
        mode: 测试模式 ('all', 'prefill', 'decode')
    """
    fieldnames = get_fieldnames_by_mode(mode)
    
    # 构建完整的数据行
    full_row = {
        'input_tokens': test_params['input_tokens'],
        'prefix_length': test_params['prefix_length'],
        'output_tokens': test_params['output_tokens'],
        'concurrency': test_params['concurrency'],
        'number': test_params['number'],
        **metrics
    }
    
    # 只保留当前mode需要的字段
    row = {k: full_row[k] for k in fieldnames}
    
    file_mode = 'w' if is_new_file else 'a'
    with open(output_file, file_mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)


def run_evalscope_perf(model_config, test_params):
    """运行单次测试
    
    Args:
        model_config: 模型配置字典
        test_params: 测试参数字典
    
    Returns:
        evalscope的测试结果
    """
    task_cfg = Arguments(
        # 模型配置
        model=model_config['model'],
        url=model_config['url'],
        api=model_config['api'],
        api_key=model_config['api_key'],
        tokenizer_path=model_config['tokenizer_path'],
        
        # 测试参数
        number=[test_params['number']],
        parallel=[test_params['concurrency']],
        rate=-1,
        
        # 输入输出长度参数
        min_prompt_length=test_params['min_prompt_length'] - test_params['prefix_length'],
        max_prompt_length=test_params['max_prompt_length'] - test_params['prefix_length'],
        min_tokens=test_params['min_tokens'],
        max_tokens=test_params['max_tokens'],
        prefix_length=test_params['prefix_length'],
        
        # 其他配置
        dataset='random',
        log_every_n_query=200000,
        extra_args={'ignore_eos': True}
    )
    
    results = run_perf_benchmark(task_cfg)
    return results


def run_auto_test(config_path):

    config = read_config(config_path)
    test_mode, result_file, model_config, concurrency_list, number_list, input_tokens, prefix_length, output_tokens = config_parser(config)
    
    is_new_file = not os.path.exists(result_file)
    
    total_test_count = len(input_tokens) * len(output_tokens) * len(concurrency_list)
    for i in range(len(input_tokens)):
        input_token = input_tokens[i]
        prefix_length = prefix_length[i]
        
        for j in range(len(output_tokens)):
            output_token = output_tokens[j]
            
            for k in range(len(concurrency_list)):
                concurrency = concurrency_list[k]
                number = number_list[k]
                current_test_count = i * j * k
                print(f"Test Mode: {test_mode} \nNo: {current_test_count}/{total_test_count} \nInput Length: {input_token} \nOutput Length: {output_token} \nConcurrency: {concurrency} \n")
                
                test_params = {
                    'number': number,
                    'concurrency': concurrency,
                    'min_prompt_length': input_token,
                    'max_prompt_length': input_token,
                    'min_tokens': output_token,
                    'max_tokens': output_token,
                    'prefix_length': prefix_length,
                    'input_tokens': input_token,
                    'output_tokens': output_token
                }
                
                try:
                    # 运行测试
                    results = run_evalscope_perf(model_config, test_params)
                    print("测试结果")
                    print(results)
                    
                    # 提取指标
                    metrics = extract_result_metrics(results)
                    
                    # 写入CSV
                    write_to_csv(result_file, test_params, metrics, is_new_file, test_mode)
                    is_new_file = False  # 第一次写入后，后续都是追加
                    
                    print(f"  ✓ 测试完成，结果已写入 {result_file}")
                    print(f"    TTFT: {metrics['ttft']:.4f}s, "
                            f"TPOT: {metrics['tpot']:.4f}s, "
                            f"Output throughput: {metrics['output_token_throughput']:.2f} tok/s")
                    
                except Exception as e:
                    print(f"  ✗ 测试失败: {str(e)}")
                    # 继续执行下一个测试
                finally:
                    # 清理evalscope生成的outputs文件夹
                    clean_outputs_folder()
    
    print(f"\n所有测试完成！结果已保存到 {result_file}")


if __name__ == "__main__":
    ## config 为输入参数
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
    args = parser.parse_args()
    config_path = args.config
    run_auto_test(config_path)
