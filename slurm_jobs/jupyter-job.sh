#! /usr/bin/env bash
export TMPDIR='/tmp'

srun \
    --job-name "$(whoami)-jupyter" \
    --partition gpuq \
    -w g003 \
    --time 9:00:00 \
    --pty bash -l -c \
    "
    ~/bigstick/.venv/bin/jupyter \
        server \
            --ip 0.0.0.0 \
            --NotebookApp.token='' \
            --NotebookApp.password='' \
            -y
    "