from typing import cast

from fakeredis.aioredis import FakeRedis

from src.core.realtime.redis_pubsub import RedisLike, RedisSubscriptionManager
from src.core.websocket.manager import ConnectionManager


def get_test_redis_subscription_manager() -> RedisSubscriptionManager:
    # Not started (.start()) — these tests only need publish() (a plain
    # `redis.publish(...)` call) to resolve without error, not real
    # cross-instance delivery. Real delivery is covered by
    # tests/integration/realtime, which uses the actual lifespan-created
    # instance instead of this override (see its `client` fixture).
    # cast: fakeredis's stubs are broader than RedisLike (extra **kwargs,
    # wider param types) so they don't structurally match despite being
    # runtime-compatible — same gap RedisDep papers over with cast(Redis, ...).
    return RedisSubscriptionManager(cast(RedisLike, FakeRedis()), ConnectionManager())
