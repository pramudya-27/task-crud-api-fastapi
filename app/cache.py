import os

from redis import Redis


def create_redis_client() -> Redis | None:
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        return None

    return Redis.from_url(
        redis_url,
        decode_responses=True,
    )