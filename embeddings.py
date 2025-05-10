from llama_index.embeddings.ollama import OllamaEmbedding
import src.config as c

ollama_embedding = OllamaEmbedding(
    model_name=c.MODEL,
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)

pass_embedding = ollama_embedding.get_text_embedding_batch(
    ["This is a passage!", "This is another passage"], show_progress=True
)
print(pass_embedding)

query_embedding = ollama_embedding.get_query_embedding("Where is blue?")
print(query_embedding)