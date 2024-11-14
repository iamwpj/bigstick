#!/usr/bin/env bash
#SBATCH --job-name=joneswac-ollama-query
#SBATCH --output=error.log

cd /home/joneswac/bigstick
.venv/bin/python main.py run --evaluation eval_3