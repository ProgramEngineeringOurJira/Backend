from datetime import timedelta

from pydantic import MongoDsn, RedisDsn
from pydantic_settings import BaseSettings

class MongoDsnSettings(BaseSettings):
    MONGO_URL: MongoDsn = "mongodb://localhost:27017"

    class Config:
        env_file = ".env"
        extra = "ignore"


class RedisSettings(BaseSettings):
    REDIS_URL: RedisDsn = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        extra = "ignore"


class ClientAPISettings(BaseSettings):
    APP_NAME: str = "Kristi"
    MAIN_URL: str = "/"
    PATH_PREFIX: str = "/v1"
    APP_HOST: str = "http://0.0.0.0"
    APP_PORT: int = 8080
    AUTH_SECRET: str
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = timedelta(hours=1).seconds
    REFRESH_TOKEN_EXPIRE_SECONDS: int = timedelta(weeks=1).seconds

    SERVER_PORT: int = 8000
    SERVER_HOST: str = "0.0.0.0"

    class Config:
        env_file = ".env"
        extra = "ignore"


class EmailSettings(BaseSettings):
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str

    TTL: int = 5 * 60

    class Config:
        env_file = ".env"
        extra = "ignore"


client_api_settings = ClientAPISettings()
mongo_settings = MongoDsnSettings(extra="ignore")
redis_settings = RedisSettings(extra="ignore")
email_settings = EmailSettings()

# TODO: сделать получение настроек через DI
