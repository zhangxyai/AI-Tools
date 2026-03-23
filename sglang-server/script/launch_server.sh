SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. 检查是否传入了两个参数
if [ $# -ne 2 ]; then
    echo "Error: Please provide sglang_launch.yaml and deploy.env file path!"
    echo "\$0 /path/to/sglang_launch.yaml /path/to/deploy.env"
    exit 1
fi


SGLANG_CONFIG_FILE="\$1"
ENV_FILE="\$2"

# 2. 检查文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "错误：文件 '$ENV_FILE' 不存在或不是一个常规文件！"
    exit 1
fi

# 3. Source 该文件
# 注意：如果文件内容有语法错误，source 会失败，这里捕获错误
if ! source "$ENV_FILE"; then
    echo "错误：加载文件 '$ENV_FILE' 失败，请检查文件内容语法。"
    exit 1
fi

echo "成功加载环境变量文件: $ENV_FILE"


if (( NNODES > 1 )); then
    echo "launch multi nodes."
    python3 -m sglang.launch_server --config $SGLANG_CONFIG_FILE --port $SERVER_PORT --base-gpu-id $BASE_GPU_ID --dist-init-addr $DIST_INIT_ADDR --nnodes $NNODES --node-rank $NODE_RANK
else
    echo "launch 1 node."
    python3 -m sglang.launch_server --config $SGLANG_CONFIG_FILE --port $SERVER_PORT --base-gpu-id $BASE_GPU_ID
fi