from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URL, DB_NAME

client: AsyncIOMotorClient | None = None
_db = None


def connect_db():
    global client, _db

    if not MONGO_URL:
        raise RuntimeError("❌ MONGO_URL is not set")

    if not DB_NAME:
        raise RuntimeError("❌ DB_NAME is not set")

    client = AsyncIOMotorClient(MONGO_URL)
    _db = client[DB_NAME]

    print(f"✅ MongoDB connected to DB: {DB_NAME}")


def close_db():
    global client

    if client:
        client.close()
        print("🛑 MongoDB connection closed")


def get_db():
    if _db is None:
        raise RuntimeError("❌ Database not initialized. Did you forget connect_db()?")

    return _db
