#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_MODE="deploy"

# 1. 检查是否传入了一个参数
if [ $# -ne 1 ]; then
    echo "错误：请提供环境变量文件路径作为参数。"
    echo "用法: \$0 <env_file_path>"
    exit 1
fi

ENV_FILE="\$1"

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

ENV_FILENAME=$(basename "$ENV_FILE")
SGLANG_CONFIG_PREFIX=/config/$MODEL_NAME/$WORKER_TYPE/$PARALLEL
SGLANG_CONFIG_FILE_PATH=$SGLANG_CONFIG_PREFIX/$CONFIG_FILENAME
ENV_CONFIG_FILE_PATH=$SGLANG_CONFIG_PREFIX/$ENV_FILENAME

if [ RUN_MODE = "test" ]; then
    docker run -itd --privileged=true --gpus all --ipc host --network host --name ${DOCKER_CONTAINER_NAME}_test \
        -v /lib/modules:/lib/modules \
        -v /dev:/dev \
        -v $HOME/.cache:/root/.cache \
        -v $MODEL_WEIGHT_PATH:/models \
        -v $SCRIPT_DIR/../config:/config \
        -v $SCRIPT_DIR:/script \
        $DOCKER_IMAGE
else
    docker run -d --restart unless-stopped --privileged=true --gpus all --ipc host --network host --name ${DOCKER_CONTAINER_NAME}_test \
        -v /lib/modules:/lib/modules \
        -v /dev:/dev \
        -v $HOME/.cache:/root/.cache \
        -v $MODEL_WEIGHT_PATH:/models \
        -v $SCRIPT_DIR/../config:/config \
        -v $SCRIPT_DIR:/script \
        $DOCKER_IMAGE bash /script/launch_server.sh $SGLANG_CONFIG_FILE_PATH $ENV_CONFIG_FILE_PATH
fi