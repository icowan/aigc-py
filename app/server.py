import argparse
import time
from importlib import metadata
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from langserve import APIHandler, add_routes
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from langchain.chat_models import ChatAnthropic, ChatOpenAI

from app.config.dependencies import get_query_token, get_token_header
from app.middleware.jwt_middleware import JWTAuthenticationBackend
from app.models.base import engine, Base, SessionLocal
from app.repository.repository import get_repository
from app.routes import datasets, assistants, chat, models

# from rag_conversation import chain as rag_conversation_chain

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

app.include_router(datasets.router, prefix="/v0")
app.include_router(assistants.router, prefix="/v0")
app.include_router(chat.router, prefix="/v0")
app.include_router(models.router, prefix="/api/models")

Base.metadata.create_all(bind=engine)

middleware = [
    # Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
    Middleware(JWTAuthenticationBackend)
]


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
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


@app.middleware("http")
async def add_tracer_middleware(request: Request, call_next):
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_auth_middleware(request: Request, call_next):
    auth = request.headers.get("Authorization")
    if auth is None:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    # db = request.state.db
    # jwt = JWTAuthenticationBackend()
    # user = jwt.authenticate(request, db)
    # if user is None:
    #     return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    # request.state.user = user
    request.state.tenant_id = 1
    request.state.email = "admin@admin.com"
    response = await call_next(request)
    return response


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
        allow_origins=args.allowed_origins,
        allow_credentials=args.allow_credentials,
        allow_methods=args.allowed_methods,
        allow_headers=args.allowed_headers,
    )
    app.middleware(middleware)

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
