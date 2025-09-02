import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect_db(cls):
        """Create database connection."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            cls.database = cls.client[settings.mongodb_database]
            
            # Create indexes for better performance
            await cls._create_indexes()
            
            logger.info("Connected to MongoDB.")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection.")

    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for better performance."""
        try:
            # Users collection indexes
            await cls.database.users.create_index([("firebase_uid", ASCENDING)], unique=True)
            await cls.database.users.create_index([("email", ASCENDING)])
            
            # SMS messages collection indexes
            await cls.database.sms_messages.create_index([("user_id", ASCENDING)])
            await cls.database.sms_messages.create_index([("timestamp", DESCENDING)])
            await cls.database.sms_messages.create_index([("sender", ASCENDING)])
            await cls.database.sms_messages.create_index([("parsed", ASCENDING)])
            
            # Transactions collection indexes
            await cls.database.transactions.create_index([("user_id", ASCENDING)])
            await cls.database.transactions.create_index([("transaction_date", DESCENDING)])
            await cls.database.transactions.create_index([("amount", ASCENDING)])
            await cls.database.transactions.create_index([("merchant", ASCENDING)])
            await cls.database.transactions.create_index([("category", ASCENDING)])
            await cls.database.transactions.create_index([("transaction_type", ASCENDING)])
            await cls.database.transactions.create_index([("reference_number", ASCENDING)])
            
            # Categories collection indexes
            await cls.database.categories.create_index([("user_id", ASCENDING)])
            await cls.database.categories.create_index([("name", ASCENDING)])
            
            # Merchants collection indexes
            await cls.database.merchants.create_index([("user_id", ASCENDING)])
            await cls.database.merchants.create_index([("name", ASCENDING)])
            
            logger.info("Database indexes created successfully.")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")


# Database collections
def get_users_collection():
    return Database.database.users

def get_sms_messages_collection():
    return Database.database.sms_messages

def get_transactions_collection():
    return Database.database.transactions

def get_categories_collection():
    return Database.database.categories

def get_merchants_collection():
    return Database.database.merchants
