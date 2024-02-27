from pydantic import BaseModel


class ChatCompletionsRequest(BaseModel):
    """
    The request for a chat completion.
    """
    content: str
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 1.0
    top_k: int = -1
    n: int = 1
    stop: list[str] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    user: str = None
