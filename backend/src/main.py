import asyncio
import contextlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import close_redis, init_redis, listen_redis_chat_expired
from src.gpt.router import gpt_router
from src.users.router import users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    await init_redis()
    listener_task = asyncio.create_task(listen_redis_chat_expired())
    yield
    listener_task.cancel()

    with contextlib.suppress(asyncio.CancelledError):
        await listener_task

    await close_redis()


app = FastAPI(lifespan=lifespan)


if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

app.include_router(users_router)
app.include_router(gpt_router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
