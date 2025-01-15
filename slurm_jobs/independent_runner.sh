#!/usr/bin/env bash
#SBATCH --partition=gpuq
#SBATCH --exclude=g00[1-2]
#SBATCH --exclusive
#SBATCH --job-name=independent-runner
#SBATCH --output=slurm_jobs/outputs/%x-%j.out
#SBATCH --error=slurm_jobs/outputs/%x-%j.err

module load docker
cd /home/joneswac/bigstick || exit 1

# Remove any randoms laying around.
docker rm -f ollama 2>/dev/null

docker pull ollama/ollama
docker run \
    --gpus=all \
    -v /home/joneswac/data/llama-data:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama &

sleep 10
.venv/bin/python main.py run --evaluation "${EVAL}"

# Remove this container.
docker rm -f ollama 2>/dev/null
