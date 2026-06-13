from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoClientSingleton:
    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None

    def __init__(self, connection_string: str, database_name: str = "text2sql") -> None:
        self._connection_string = connection_string
        self._database_name = database_name

    async def connect(self) -> None:
        if MongoClientSingleton._client is None:
            MongoClientSingleton._client = AsyncIOMotorClient(self._connection_string)
            MongoClientSingleton._database = MongoClientSingleton._client[self._database_name]

    async def disconnect(self) -> None:
        if MongoClientSingleton._client is not None:
            MongoClientSingleton._client.close()
            MongoClientSingleton._client = None
            MongoClientSingleton._database = None

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if MongoClientSingleton._database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return MongoClientSingleton._database

    @property
    def client(self) -> AsyncIOMotorClient:
        if MongoClientSingleton._client is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return MongoClientSingleton._client
