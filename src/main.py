import asyncio

import redis.exceptions
from arq import create_pool
from fastapi import FastAPI, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from src.api.task_routers import router as task_router
from src.core.config import AppSettings, redis_settings
from src.core.logger import logger

app = FastAPI(**AppSettings().dict())
app.include_router(task_router, prefix="/tasks", tags=["tasks"])

REDIS_RETRY_SECONDS = 2
REDIS_RETRY_ATTEMPTS = 10


@app.on_event("startup")
async def startup():
    for attempt in range(1, REDIS_RETRY_ATTEMPTS + 1):
        try:
            app.state.redis = await create_pool(redis_settings)
            break
        except (OSError, ConnectionError, TimeoutError, redis.exceptions.TimeoutError) as e:
            if attempt == REDIS_RETRY_ATTEMPTS:
                logger.error("Redis connection failed after %s attempts: %s", REDIS_RETRY_ATTEMPTS, e)
                raise
            logger.warning("Redis not ready (attempt %s/%s), retrying in %ss...", attempt, REDIS_RETRY_ATTEMPTS, REDIS_RETRY_SECONDS)
            await asyncio.sleep(REDIS_RETRY_SECONDS)


@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error("Validation error on path %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()[0]["msg"]},
    )
