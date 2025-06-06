import os
from dotenv import load_dotenv

# Load Local
expected_env = f"{os.getcwd()}/.env"
if os.path.exists(expected_env):
    load_dotenv(expected_env)

GPU_NODE = os.environ.get("GPU_NODE")
TRIALS = int(os.environ.get("TRIALS", 1))
DATA_PATH = os.environ.get("DATA_PATH", "data")
DB_FILE = os.environ.get("DB_FILE", f"{DATA_PATH}/reports.sqlite3")
JOB_NAME = os.environ.get("JOB_NAME", None)
RESULTS_PATH = os.environ.get("RESULTS_PATH", "results")
LANGCHAIN_TRACING_V2 = os.environ.get("LANGCHAIN_TRACING_V2", None)
LANGCHAIN_ENDPOINT = os.environ.get("LANGCHAIN_ENDPOINT", None)
LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY", None)
MAX_TOKENS = os.environ.get("MAX_TOKENS", 131072)
STATE_FILE = os.environ.get("STATE_FILE", f"{DATA_PATH}/state.pkl")
MODELS_PATH = os.environ.get("MODELS_PATH", f"{DATA_PATH}/models")
MODEL = os.environ.get("MODEL")
LLAMA_CPP_PORT = int(os.environ.get("LLAMA_CPP_PORT", 8080))
