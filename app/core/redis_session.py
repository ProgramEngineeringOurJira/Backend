import redis.asyncio as redis

from app.config import email_settings, redis_settings
from app.routers.auth.schemas import UserRegister

# UserRegister перенесён сюда из app.routes.auth, так как там он зацикливался


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

    async def set_uuid_email(self, uuid: str, user: UserRegister) -> None:
        await self.con.set(uuid, user.model_dump_json())
        await self.con.expire(uuid, email_settings.TTL)

    async def get_user(self, uuid: str) -> UserRegister:
        return await self.con.get(uuid)
