#!/usr/bin/env bash

srun \
    --job-name ollama-container-run \
    --partition gpuq \
    --pty \
    bash -l -c \
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