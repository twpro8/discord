from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.kernel.config import settings
from src.kernel.errors import LumiereError, app_exception_handler
from src.kernel.logging import configure_logging, get_logger
from src.kernel.redis import close_redis, init_redis
from src.kernel.router import api_router
from src.utils import custom_generate_unique_id

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # --- Startup ---
    configure_logging()
    logger.info("app.startup", env=settings.ENVIRONMENT)

    # Initialize Redis connection pool
    app.state.redis = await init_redis()

    yield

    # --- Shutdown ---
    logger.info("app.shutdown")

    # Gracefully close Redis connection
    await close_redis(app.state.redis)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALL_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(LumiereError, app_exception_handler)  # type: ignore
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
