#!/usr/bin/env bash
export TMPDIR='/tmp'

# shellcheck source=/dev/null
source .env

node=${GPU_NODE:-g005}
sess=${SESSION_FILE:-'~/bigstick/.ssh-session'}

if [ -f './kill-llama.cpp.sh' ]; then
    # shellcheck source=/dev/null
    source kill-llama.cpp.sh
fi

ssh -f -N -M \
    -S "$sess" \
    -o ExitOnForwardFailure=yes\
    -L "${LLAMA_CPP_PORT}:localhost:${LLAMA_CPP_PORT}" "$node"

cat << EOT > ./kill-llama.cpp.sh
#!/usr/bin/env bash
# Session at $(date)
ssh -S $sess -O exit $node
srun \
    --job-name container-killer \
    --partition gpuq \
    -w "$node" \
    --pty bash -l -c\
    "
    module load docker
    docker rm -f llama.cpp 2>/dev/null
    "
rm -- kill-llama.cpp.sh
EOT

chmod a+x kill-llama.cpp.sh

srun \
    --job-name container-killer \
    --partition gpuq \
    -w "$node" \
    --pty bash -l -c\
    "
    module load docker
    docker rm -f llama.cpp 2>/dev/null
    "

srun \
    --job-name llama.cpp-container-run \
    --partition gpuq \
    -w "$node" \
    --pty bash -l -c \
    "
    module load docker && \
    docker run \
        --rm -it \
        --gpus=all \
        -v ${MODELS_PATH}:/models/ \
        -p ${LLAMA_CPP_PORT}:${LLAMA_CPP_PORT} \
        --name llama.cpp \
        ghcr.io/ggerganov/llama.cpp:server-cuda \
            -m /models/${MODEL} \
            --port ${LLAMA_CPP_PORT} \
            --metrics
            -ngl 81
            -c ${MAX_TOKENS}
    "