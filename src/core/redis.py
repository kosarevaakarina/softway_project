from arq import ArqRedis
from fastapi import Request


def get_redis(request: Request) -> ArqRedis:
    return request.app.state.redis
