DOCKER_IMAGE=lmsysorg/sgl-model-gateway:v0.3.2
CONTAINER_NAME=sgl-model-gateway
ROUTER_PORT=8000
MODEL_PATH=$HOME/workspace

prefill_urls=(
    "http://10.119.194.202:30000"
    "http://10.119.194.203:30000"
)
decode_urls=(
    "http://10.119.194.204:30000"
    "http://10.119.194.205:30000"
    "http://10.119.194.206:30000"
    "http://10.119.194.207:30000"
)

prefill_args=""
decode_args=""
for url in "${prefill_urls[@]}"; do
    prefill_args+=" --prefill ${url}"
done
for url in "${decode_urls[@]}"; do
    decode_args+=" --decode ${url}"
done
echo "prefill_args: ${prefill_args}"
echo "decode_args: ${decode_args}"

docker run -itd --restart unless-stopped --gpus all \
    --ipc=host --privileged=true --network host --name $CONTAINER_NAME \
    -v /lib/modules:/lib/modules \
    -v /dev:/dev \
    -v $MODEL_PATH:/models \
    -v /root/.cache:/root/.cache \
    $DOCKER_IMAGE \
        python -m sglang_router.launch_router \
        --pd-disaggregation \
        ${prefill_args} \
        ${decode_args} \
        --host 0.0.0.0 \
        --max-concurrent-requests 4096 \
        --health-check-interval-secs 5 \
        --policy round_robin \
        --backend openai \
        --port $ROUTER_PORT