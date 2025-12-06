import pymongo
import logging
from config import MONGO_URI, DB_NAME

client = None
db = None
students_collection = None
mongodb_available = False

try:
  client = pymongo.MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000
  )
  client.admin.command("ping")  # force connection
  db = client[DB_NAME]
  students_collection = db["students"]
  mongodb_available = True
  logging.info("✅ Connected to MongoDB")
except Exception as e:
  logging.error(f"❌ MongoDB connection failed: {str(e)}")
