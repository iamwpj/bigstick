#!/usr/bin/env bash

srun \
    --job-name generating-logs-container \
    --partition defq \
    --pty \
    bash -l -c \
    "
    module load docker
    docker run \
        --rm -it \
        --name flog \
            mingrammer/flog \
            -f apache_combined \
            -n 1000 \
            > ~/data/llama-data/logs/generated.log
    "