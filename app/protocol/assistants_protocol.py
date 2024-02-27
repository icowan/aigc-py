from typing import Optional, Union, List

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class AssistantsChatCompletionsRequest(BaseModel):
    """
    The request for a chat completion.
    """
    messages: list[dict[str, str]] = Field(
        ...,
        description="A list of messages to be used as context for the completion.",
    )
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    top_k: Optional[int] = -1
    n: Optional[int] = 1
    max_tokens: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class AssistantsChatCompletionsResponse:
    """
    The response for a chat completion.
    """
    choices: list[dict[str, str]] = Field(
        ...,
        description="A list of completions."
    )
    model_id: str = Field(
        ...,
        description="The model used to generate the completions."
    )
    created_at: str = Field(
        ...,
        description="The time the completion was created."
    )
    updated_at: str = Field(
        ...,
        description="The time the completion was updated."
    )
