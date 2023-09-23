import redis.asyncio as redis

from app.config import redis_settings


class Redis:

    con: redis.Redis = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Redis, cls).__new__(cls)
        return cls.instance

    @classmethod
    async def connect_redis(cls) -> None:
        cls.con = None
        cls.con = redis.from_url(str(redis_settings.REDIS_URL), encoding="utf-8", decode_responses=True)

    @classmethod
    async def disconnect_redis(cls) -> None:
        if cls.con:
            await cls.con.close()
