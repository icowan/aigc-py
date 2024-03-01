import argparse
import time
from importlib import metadata

from jose import jwt, JWTError
from fastapi import Depends, FastAPI, Request, Response, HTTPException, Security
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.config.config import get_config
from app.logger.logger import get_logger
from app.middleware.trace_middleware import TraceMiddleware
from app.models.base import engine, Base, SessionLocal, get_db
from app.protocol.api_protocol import ErrorResponse
from app.repository.repository import get_repository
from app.routes import datasets, data_annotation

PYDANTIC_VERSION = metadata.version("pydantic")
_PYDANTIC_MAJOR_VERSION: int = int(PYDANTIC_VERSION.split(".")[0])

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
    dependencies=[
        # Depends(get_token_header),
        # Depends(get_query_token),
    ]
)

app_config = get_config()

logger = get_logger("server")

store = get_repository(SessionLocal)

# security = HTTPBearer()


# async def get_current_user(token: HTTPAuthorizationCredentials = Security(security)):
#     try:
#         payload = jwt.decode(token.credentials, app_config.app_secret_key, algorithms=["HS256"])
#         email: str = payload.get("email")
#         if email is None:
#             raise HTTPException(status_code=403, detail="Could not validate credentials")
#         return {"email": email}
#     except JWTError:
#         raise HTTPException(status_code=403, detail="Could not validate credentials")


app.include_router(datasets.router, prefix="/mgr")
app.include_router(data_annotation.router, prefix="/mgr")

# app.include_router(assistants.router, prefix="/v0")
# app.include_router(chat.router, prefix="/v0")
# app.include_router(models.router, prefix="/api/models")

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    # if not request.headers.get("Authorization") and request.headers.get("X-Token"):
    #     request.headers["Authorization"] = request.headers["X-Token"]
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_auth_middleware(request: Request, call_next):
    auth = request.headers.get("Authorization")
    x_auth = request.headers.get("X-Token")
    if auth is None and x_auth is None:
        return ErrorResponse(message="Unauthorized", code=401)

    # 优先取 auth 如果auth把x_auth赋给auth
    token = auth if auth else x_auth
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    # token = "Bearer " + token
    try:
        payload = jwt.decode(token, app_config.app_secret_key, algorithms=[app_config.app_algorithm])
    except JWTError as e:
        logger.warn(f"Unauthorized token: {token}, error_msg: {e}")
        return ErrorResponse(message="Unauthorized", code=401)

    request.state.tenant_id = 1
    request.state.email = payload.get("email")
    response = await call_next(request)
    return response


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        request.state.store = get_repository(request.state.db)
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warn(exc.detail)
    return JSONResponse(
        status_code=200,
        content=ErrorResponse(
            message=exc.detail,
            code=exc.status_code,
        ).dict(),
    )


@app.get("/docs")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
# add_routes(app, NotImplemented)
# add_routes(app, rag_conversation_chain, path="/rag_conversation")
# add_routes(
#     app,
#     ChatOpenAI(),
#     path="/openai",
# )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AIGC RESTful API server."
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host name")
    parser.add_argument("--port", type=int, default=8000, help="port number")
    # parser.add_argument("--openai_base_url", type=str, default=OPENAI_API_BASE_URL, help="OpenAI API Base URL")
    # parser.add_argument("--openai_api_key", type=str, default=OPENAI_API_KEY, help="OpenAI API Key")

    args = parser.parse_args()

    app.add_middleware(
        CORSMiddleware,
        # allow_origins=args.allowed_origins,
        # allow_credentials=args.allow_credentials,
        # allow_methods=args.allowed_methods,
        # allow_headers=args.allowed_headers,
    )
    app.add_middleware(TraceMiddleware)

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
