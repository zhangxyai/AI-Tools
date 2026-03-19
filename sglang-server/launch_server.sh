SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


NODE_RANK=0
NNODES=2
DIST_INIT_ADDR=172.26.168.30:45000

SERVER_PORT=30000
BASE_GPU_ID=0
SGLANG_CONFIG_PREFIX=config/deepseek-v32/decode/decode-dp16ep16
SGLANG_CONFIG_FILE=$SCRIPT_DIR/$SGLANG_CONFIG_PREFIX.yaml
SGLANG_ENV_FILE=$SCRIPT_DIR/$SGLANG_CONFIG_PREFIX.env

# 判断文件是否存在
if [ -f "$SGLANG_ENV_FILE" ]; then
    echo "source success: $SGLANG_ENV_FILE"
    source $SGLANG_ENV_FILE
fi

if (( NNODES > 1 )); then
    echo "launch multi nodes."
    python3 -m sglang.launch_server --config $SGLANG_CONFIG_FILE --port $SERVER_PORT --base-gpu-id $BASE_GPU_ID --dist-init-addr $DIST_INIT_ADDR --node-rank $NODE_RANK
else
    echo "launch 1 node."
    python3 -m sglang.launch_server --config $SGLANG_CONFIG_FILE --port $SERVER_PORT --base-gpu-id $BASE_GPU_ID
fi