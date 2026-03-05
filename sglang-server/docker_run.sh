DOCKER_CONTAINER_NAME=deepseek-v32
MODEL_PATH=$HOME/workspace
DOCKER_IMAGE=lmsysorg/sglang:v0.5.9


docker run -itd --privileged=true --gpus all --ipc host --network host --name $DOCKER_CONTAINER_NAME\
    -v /lib/modules:/lib/modules \
    -v /dev:/dev \
    -v $MODEL_PATH:/models \
    $DOCKER_IMAGE