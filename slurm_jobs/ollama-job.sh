#!/usr/bin/env bash
export TMPDIR='/tmp'

# shellcheck source=/dev/null
source ".env"

node=${GPU_NODE:-g001}
sess=${SESSION_FILE:-'~/bigstick/.ssh-session'}

if [ -f './kill-ollama.sh' ]; then
    # shellcheck source=/dev/null
    source kill-ollama.sh
fi

ssh -f -N -M \
    -S "$sess" \
    -o ExitOnForwardFailure=yes\
    -L 11434:localhost:11434 "$node"

cat << EOT > ./kill-ollama.sh
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
    docker rm -f ollama 2>/dev/null
    "
rm -- kill-ollama.sh
EOT

chmod a+x kill-ollama.sh

srun \
    --job-name container-killer \
    --partition gpuq \
    -w "$node" \
    --pty bash -l -c\
    "
    module load docker
    docker rm -f ollama 2>/dev/null
    "

srun \
    --job-name ollama-container-run \
    --partition gpuq \
    -w "$node" \
    --pty bash -l -c \
    "
    module load docker && \
    docker pull ollama/ollama
    docker run \
        --rm -it \
        --gpus=all \
        -v /home/joneswac/data/llama-data:/root/.ollama \
        -p 11434:11434 \
        --name ollama \
        ollama/ollama
    "
