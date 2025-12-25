# app/core/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URL, DB_NAME

client: AsyncIOMotorClient | None = None
db = None


def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]


def close_db():
    global client
    if client:
        client.close()
