import time
from typing import List, Optional, Literal

import shortuuid
from langchain_core.messages import ChatMessage
from pydantic import BaseModel, Field


class ChatCompletionResponseChoice:
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length"]] = None


class UsageInfo:
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{shortuuid.random()}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo
