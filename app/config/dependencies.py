import logging

from fastapi import Header, HTTPException

from app.protocol.api_protocol import ErrorResponse


async def get_token_header(x_token: str = Header(...), host: str = Header(...)):
    if not x_token:
        logging.warning(f"X-Token header invalid: {x_token}")
        raise ErrorResponse(message="X-Token header invalid", code=401)
    if not host:
        logging.warning(f"Host header invalid: {host}")
        raise ErrorResponse(message="Host header invalid", code=401)
    # try:
    #     payload = jwt.decode(x_token, get_config().jwt_secret, algorithms=["HS256"])
    #     return ChatUser(**payload)
    # except JWTError as e:
    #     logging.warning(f"parse token error: {x_token}, error_msg: {e}")
    #     raise BusinessError(message="请先登录", code=401)


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")
