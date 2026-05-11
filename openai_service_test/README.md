# 模型服务功能测试工具

分为四种测试模型
test_mode: "simple"               测试reasoning parser是否正常解析
test_mode: "struct_output"        测试struct_output是否正常输出
test_mode: "funcation_call"       测试tool calls是否正常调用
test_mode: "all"                  默认，依次进行上述三项测试

## 使用说明

1. 安装依赖

```bash
pip3 install -r requirements.txt
```

2. 按注释提示修改config.yaml配置文件

3. 启动测试脚本

```bash
python3 test_chat_completions.py
```
