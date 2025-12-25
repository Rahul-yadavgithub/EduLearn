# app/core/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URL, DB_NAME

client: AsyncIOMotorClient | None = None
db = None


def connect_db():
    global client, db

    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)

    if db is None:
        db = client[DB_NAME]

    print("✅ MongoDB connected:", DB_NAME)


def close_db():
    global client

    if client:
        client.close()
        print("🛑 MongoDB connection closed")
