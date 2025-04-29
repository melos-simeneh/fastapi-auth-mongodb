from motor.motor_asyncio import AsyncIOMotorClient
from utils.settings import MONGO_URI


class MongoDBConnection:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(MONGO_URI)
            await self.client.admin.command('ping')
            self.db = self.client["auth_db_3"]
            self.users_collection = self.db["users"]
            print("✅ MongoDB connected")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False

    async def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

mongo_connection = MongoDBConnection()