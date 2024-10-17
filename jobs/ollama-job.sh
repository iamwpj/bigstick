#!/usr/bin/env bash
export TMPDIR='/tmp'

source .env

node=${GPU_NODE:-g001}
sess=${SESSION_FILE:-'~/bigstick/.ssh-session'}

if [ -f './kill.sh' ]; then
    source kill.sh
fi

ssh -f -N -M \
    -S "$sess" \
    -o ExitOnForwardFailure=yes\
    -L 11434:localhost:11434 "$node"

echo -e "#!/usr/bin/env bash
# Session at $(date)
ssh -S $sess -O exit $node
rm -- kill.sh
" > ./kill.sh

chmod a+x kill.sh

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
    --time 9:00:00 \
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
