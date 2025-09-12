"""
GridFS Service - Handles all GridFS operations
Separates database logic from controller logic
"""
from flask import current_app
from db import init_db
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import io
import base64

class GridFSService:
    """Service class for GridFS operations"""
    
    def __init__(self):
        self._fs = None
        self._db = None
    
    def _get_connection(self):
        """Get GridFS and database connection"""
        if self._fs is None or self._db is None:
            client, db, fs = init_db(current_app)
            self._fs = fs
            self._db = db
        return self._fs, self._db
    
    def upload_file(self, file_data, filename, metadata):
        """Upload a file to GridFS"""
        fs, db = self._get_connection()
        file_id = fs.put(file_data, filename=filename, metadata=metadata)
        return file_id
    
    def get_file(self, file_id):
        """Get file data from GridFS"""
        fs, db = self._get_connection()
        return fs.get(file_id).read()
    
    def get_file_info(self, file_id):
        """Get file metadata from GridFS"""
        fs, db = self._get_connection()
        return fs.find_one({'_id': file_id})
    
    def find_files(self, query):
        """Find files in GridFS with given query"""
        fs, db = self._get_connection()
        return list(fs.find(query))
    
    def delete_file(self, file_id):
        """Delete file from GridFS"""
        fs, db = self._get_connection()
        fs.delete(file_id)
    
    def validate_object_id(self, id_string):
        """Validate ObjectId format"""
        try:
            return ObjectId(id_string)
        except (InvalidId, TypeError):
            raise ValueError(f"Invalid ObjectId format: {id_string}")

# Global service instance
gridfs_service = GridFSService()
