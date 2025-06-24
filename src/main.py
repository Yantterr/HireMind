from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import close_redis, init_redis
from src.users.router import users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Life span of redis."""
    await init_redis()
    yield
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


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
