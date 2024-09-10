from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings

Settings.embed_model = OllamaEmbedding()

index = VectorStoreIndex.from_documents()