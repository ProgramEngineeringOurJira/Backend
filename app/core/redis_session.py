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

    async def set_uuid_email(self, uuid: str, user: list) -> None:
        await self.con.set(uuid, user)
        await self.con.expire(uuid, 5*60)

    async def get_uuid(self, user: list) -> str:
        return await self.con.get(user)
    
    async def get_user(self, uuid: str) -> list:
        return await self.con.get(uuid)
