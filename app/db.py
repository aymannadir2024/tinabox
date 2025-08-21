from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

_client: Optional[AsyncIOMotorClient] = None
_db = None

async def connect_to_mongo(uri: str):
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(uri)
        _db = _client.get_default_database()  # كيستعمل اسم الداتابيز من آخر الURI (مثلاً tinabox)
        print("[mongo] connected")

async def close_mongo():
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("[mongo] closed")

def get_db():
    if _db is None:
        raise RuntimeError("Mongo not connected")
    return _db
