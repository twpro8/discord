from fakeredis.aioredis import FakeRedis

from src.core.cache import Cache, RedisCache


def get_test_cache() -> Cache:
    return RedisCache(FakeRedis())
