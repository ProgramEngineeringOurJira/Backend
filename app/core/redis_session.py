import redis.asyncio as redis
from pydantic import EmailStr

from app.config import email_settings, redis_settings
from app.schemas.models.auth import UserRegister


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
        user = await self.con.get(uuid)
        await self.con.delete(uuid)
        return user

    async def set_uuid_invite_email(self, uuid: str, email: EmailStr):
        await self.con.set(uuid, email)
        await self.con.expire(uuid, email_settings.TTL)

    async def get_invite_user_email(self, uuid: str):
        email = await self.con.get(uuid)
        return email
