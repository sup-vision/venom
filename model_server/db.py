import pymongo
import logging
from pymongo import MongoClient
import gridfs
import mongoengine as me
from config import MONGO_URI, DB_NAME

client = None
db = None
students_collection = None
files_collection = None
fs = None
mongodb_available = False

def init_db(app=None):
    """Initialize database connection with GridFS and MongoEngine support"""
    global client, db, students_collection, files_collection, fs, mongodb_available
    
    try:
        # Use app config if provided, otherwise use module config
        if app:
            uri = app.config['MONGO_URI']
        else:
            uri = MONGO_URI
            
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
        client.admin.command("ping")  # force connection
        
        # This line extracts the database name from the MongoDB URI.
        # It splits the URI string at the last '/' character and takes the part after it as the database name.
        # If there is no '/' in the URI, it defaults to 'venom'.
        dbname = uri.rsplit('/', 1)[-1] if '/' in uri else 'venom'
        db = client[dbname]
        
        # GridFS bucket wrapper
        fs = gridfs.GridFS(db)
        
        # ensure index to speed metadata lookups
        # Create an index on the 'metadata._id' field in ascending order (1)
        # This speeds up queries that filter or sort by user_id in the GridFS files collection
        try:
            db.fs.files.create_index([('metadata._id', 1)])
        except Exception:
            # If index creation fails (e.g., index already exists), silently continue
            pass
        
        # connect mongoengine (for models)
        me.connect(db=dbname, host=uri)
        
        # Set up collections
        students_collection = db["students"]
        files_collection = db["files"]
        mongodb_available = True
        logging.info("✅ Connected to MongoDB with GridFS and MongoEngine")
        return client, db, fs
    except Exception as e:
        logging.error(f"❌ MongoDB connection failed: {str(e)}")
        mongodb_available = False
        return None, None, None

# Initialize on import (without app parameter)
init_db()
