DOCKER_CONTAINER_NAME=deepseek-v32
MODEL_PATH=$HOME/workspace
SGLANG_CONFIG_PATH=/mnt/afswhw1/AI-Tools/sglang-server/config
DOCKER_IMAGE=lmsysorg/sglang:v0.5.9


docker run -itd --privileged=true --gpus all --ipc host --network host --name $DOCKER_CONTAINER_NAME\
    -v /lib/modules:/lib/modules \
    -v /dev:/dev \
    -v $HOME/.cache:/root/.cache \
    -v $MODEL_PATH:/models \
    -v $SGLANG_CONFIG_PATH:/config \
    $DOCKER_IMAGE