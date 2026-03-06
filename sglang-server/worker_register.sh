#!/bin/bash
ROUTER_PORT=8000

# 检查参数数量是否为 2
if [ "$#" -ne 2 ]; then
    echo "错误: 参数数量不正确。"
    echo "用法: \$0 <worker_url> <worker_type>"
    echo "示例: \$0 http://0.0.0.0:30000 prefill"
    exit 1
fi

WORKER_URL=$1
WORKER_TYPE=$2

# 检查 worker_type 是否合法
# 定义允许的列表
VALID_WORKER_TYPES=("prefill" "decode" "regular")
TYPE_OK=false

for type in "${VALID_WORKER_TYPES[@]}"; do
    if [ "$WORKER_TYPE" == "$type" ]; then
        TYPE_OK=true
        break
    fi
done

if [ "$TYPE_OK" = false ]; then
    echo "错误: worker_type 参数无效。"
    echo "允许的值为: prefill, decode, regular"
    echo "当前输入: $WORKER_TYPE"
    exit 1
fi

# 检查 URL 格式 (简单检查是否以 http:// 或 https:// 开头)
if [[ ! "$WORKER_URL" =~ ^https?:// ]]; then
    echo "错误: URL 格式无效。"
    echo "URL 必须以 http:// 或 https:// 开头。"
    echo "当前输入: $WORKER_URL"
    exit 1
fi

# ================= 执行指令部分 =================

echo "参数校验通过，正在发送请求..."
echo "URL: $WORKER_URL"
echo "Type: $WORKER_TYPE"

# 执行 curl 命令
# 使用双引号定义 JSON 数据，内部引号使用 \" 进行转义
curl -X POST http://localhost:${ROUTER_PORT}/workers \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"${WORKER_URL}\",\"worker_type\":\"${WORKER_TYPE}\"}"
