from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

HF_TOKEN = open('.token','r').read()

documents = SimpleDirectoryReader("./llama-data/logs").load_data()

# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama
Settings.llm = Ollama(model="llama3.1:latest", request_timeout=360.0)

index = VectorStoreIndex.from_documents(
    documents,
)

query="""
This data should be read line by line. 
Each line is a separte log. The logs can be similar to eachother, but some may be different. 

You will find anomalies in the data. 
There may be no anomalies. 
There may be one anomaly. 
There may be many anomalies. 

Identify what kind of log the line you're looking at is.

An anomaly could be a repeated line.
An anomaly could be a common error related to the message source on the line without being compared to other lines.
An anomaly could be a line that doesn't match the expected format for the kind of log this is.

Before deciding if an anamoly has occured re-check the logic against the data and line to verify.

Please tell me what this log is from.
Please tell me how many anomalies, if any, there are. 
Please show me the lines that contain anomalies in the data. 

"""

query_engine = index.as_query_engine()
response = query_engine.query(query)
print(response)