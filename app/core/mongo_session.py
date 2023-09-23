from motor.motor_asyncio import AsyncIOMotorClient

from app.config import mongo_settings


class MongoManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def get_async_client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(mongo_settings.DATABASE_URL)
