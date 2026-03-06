DOCKER_IMAGE=lmsysorg/sgl-model-gateway:v0.3.2
CONTAINER_NAME=sgl-model-gateway
ROUTER_PORT=8000
MODEL_PATH=$HOME/workspace

docker run -itd --privileged=true --restart unless-stopped --ipc host --network host --name $CONTAINER_NAME \
    -v /lib/modules:/lib/modules \
    -v /dev:/dev \
    -v $MODEL_PATH:/models \
    $DOCKER_IMAGE \
    --pd-disaggregation \
    --host 0.0.0.0 \
    --port $ROUTER_PORT \
    --health-check-interval-secs 5 \
    --policy round_robin \
    --backend openai 