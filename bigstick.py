from llama_index.llms.ollama import Ollama
from llama_index.core.bridge.pydantic import BaseModel
# from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage


class AnomalyResults(BaseModel):
    """A holder for basic anomaly results."""

    line: int
    data: str
    rank: int


class LoadedModel:
    def __init__(
        self,
        model: str = "bigstick:latest",
        timeout: float = 600.0,
        json_mode=False,
        base_url="http://localhost:11434",
    ):
        self.llm = Ollama(
            model=model, request_timeout=timeout, json_mode=json_mode, base_url=base_url
        )

    def Simple(self, query: str):
        return self.llm.complete(query)

    def StructChat(self, query: str):
        sllm = self.llm.as_structured_llm(AnomalyResults)
        return sllm.chat([ChatMessage(role="user", content=query)])
