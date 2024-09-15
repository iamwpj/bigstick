from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama


documents = SimpleDirectoryReader("./llama-data/data/apache_logs/").load_data()

# Add embeddings
Settings.embed_model = OllamaEmbedding(
    model_name="llama3.1:70b", base_url="http://g005:11434"
)

# ollama
Settings.llm = Ollama(model="llama3.1:70b", request_timeout=360.0)

index = VectorStoreIndex.from_documents(
    documents,
)

query = """
Describe any anomalies or security concerns with the logs contained in this file.
"""

query_engine = index.as_query_engine()
response = query_engine.query(query)
print(response)
