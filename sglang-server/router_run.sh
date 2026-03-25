DOCKER_IMAGE=lmsysorg/sgl-model-gateway:v0.3.2
ROUTER_PORT=8000
MODEL_PATH=$HOME/models
HUGGINGFACE_DIR_NAME=DeepSeek-V3.2
CONTAINER_NAME=sgl-model-gateway-$HUGGINGFACE_DIR_NAME


prefill_urls=(
    "http://172.26.168.32:30000"
)
decode_urls=(
    "http://172.26.168.33:30000"
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

docker run -itd --restart unless-stopped \
    --ipc=host --privileged=true --network host --name $CONTAINER_NAME \
    -v /lib/modules:/lib/modules \
    -v /dev:/dev \
    -v $MODEL_PATH:/models \
    -v /root/.cache:/root/.cache \
    $DOCKER_IMAGE \
	--model-path /models/$HUGGINGFACE_DIR_NAME \
        --pd-disaggregation \
        ${prefill_args} \
        ${decode_args} \
        --host 0.0.0.0 \
	    --port $ROUTER_PORT \
        --max-concurrent-requests 4096 \
        --health-check-interval-secs 5 \
        --prefill-policy bucket
