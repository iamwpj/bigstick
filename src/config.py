import os
from dotenv import load_dotenv

# Load Local
expected_env = f"{os.getcwd()}/.env"
if os.path.exists(expected_env):
    load_dotenv(expected_env)

GPU_NODE = os.environ.get("GPU_NODE")
TRIALS = int(os.environ.get("TRIALS"))
DATA_PATH = os.environ.get("DATA_PATH", "data")
RESULTS_PATH = os.environ.get("RESULTS_PATH", "results")
