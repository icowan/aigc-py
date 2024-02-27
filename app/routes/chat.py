from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.logger.logger import build_logger
from app.models.base import get_db
from app.protocol.chat_protocol import ChatCompletionsRequest

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

logger = build_logger("assistants", "chat.log")


@router.post("/{conversationId}/completions", tags=["chat"])
async def chat_completions(conversationId: str, request: ChatCompletionsRequest, db: Session = Depends(get_db)):
    logger.info(f"Received chat completion request for conversation {conversationId}")
    return {"conversationId": conversationId, "request": request}
