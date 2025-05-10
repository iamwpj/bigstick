import requests
import json
from llama_index.llms.ollama import Ollama
from llama_index.core.bridge.pydantic import BaseModel
import src.config as c

# from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage, CompletionResponse


class AnomalyResults(BaseModel):
    """A holder for basic anomaly results."""

    line: int
    data: str
    rank: int
    explaination: str


class LoadedModel:
    def __init__(
        self,
        model: str = c.MODEL,
        timeout: float = 120.0,
        json_mode: bool = False,
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        self.llm = Ollama(
            model=model,
            request_timeout=timeout,
            json_mode=json_mode,
            base_url=base_url,
            **kwargs
        )

    def Simple(self, query: str) -> CompletionResponse:
        return self.llm.complete(query)

    def StructChat(self, query: str):
        sllm = self.llm.as_structured_llm(AnomalyResults)
        return sllm.chat([ChatMessage(role="user", content=query)])


def GenericAPI(
    url: str = "http://localhost:11434/api/",
    verb: str = "GET",
    data: dict = None,
    headers: dict = None,
) -> requests.Response:
    s = requests.Session()
    req = requests.Request(verb, url=url, data=json.dumps(data))
    prepped = s.prepare_request(req)
    if data:
        prepped.data = data

    if headers:
        prepped.headers = data
    return s.send(prepped)
