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
import logging

class GridFSService:
    """Service class for GridFS operations"""
    
    def __init__(self):
        self._fs = None
        self._db = None
    
    def _get_connection(self):
        """Get GridFS and database connection"""
        if self._fs is None or self._db is None:
            try:
                client, db, fs = init_db(current_app)
                self._fs = fs
                self._db = db
                logging.info("✅ GridFS connection established")
            except Exception as e:
                logging.error(f"❌ Failed to establish GridFS connection: {e}")
                raise
        return self._fs, self._db
    
    def upload_file(self, file_data, filename, metadata=None):
        """
        Upload a file to GridFS
        
        Args:
            file_data (bytes): File data to upload
            filename (str): Name of the file
            metadata (dict): Optional metadata for the file
            
        Returns:
            ObjectId: The ID of the uploaded file
        """
        try:
            fs, db = self._get_connection()
            
            # Add timestamp to metadata
            if metadata is None:
                metadata = {}
            metadata['uploaded_at'] = datetime.utcnow()
            
            file_id = fs.put(file_data, filename=filename, metadata=metadata)
            logging.info(f"✅ File uploaded successfully: {filename} (ID: {file_id})")
            return file_id
        except Exception as e:
            logging.error(f"❌ Failed to upload file {filename}: {e}")
            raise
    
    def get_file(self, file_id):
        """
        Get file data from GridFS
        
        Args:
            file_id (str or ObjectId): ID of the file to retrieve
            
        Returns:
            bytes: File data
        """
        try:
            fs, db = self._get_connection()
            file_id = self.validate_object_id(file_id)
            
            file_data = fs.get(file_id).read()
            logging.info(f"✅ File retrieved successfully: {file_id}")
            return file_data
        except Exception as e:
            logging.error(f"❌ Failed to get file {file_id}: {e}")
            raise
    
    def get_file_info(self, file_id):
        """
        Get file metadata from GridFS
        
        Args:
            file_id (str or ObjectId): ID of the file
            
        Returns:
            dict: File metadata and information
        """
        try:
            fs, db = self._get_connection()
            file_id = self.validate_object_id(file_id)
            
            file_info = fs.find_one({'_id': file_id})
            if file_info is None:
                raise ValueError(f"File not found: {file_id}")
            
            logging.info(f"✅ File info retrieved: {file_id}")
            return file_info
        except Exception as e:
            logging.error(f"❌ Failed to get file info {file_id}: {e}")
            raise
    
    def find_files(self, query):
        """
        Find files in GridFS with given query
        
        Args:
            query (dict): MongoDB query to find files
            
        Returns:
            list: List of file documents matching the query
        """
        try:
            fs, db = self._get_connection()
            files = list(fs.find(query))
            logging.info(f"✅ Found {len(files)} files matching query")
            return files
        except Exception as e:
            logging.error(f"❌ Failed to find files: {e}")
            raise
    
    def delete_file(self, file_id):
        """
        Delete file from GridFS
        
        Args:
            file_id (str or ObjectId): ID of the file to delete
        """
        try:
            fs, db = self._get_connection()
            file_id = self.validate_object_id(file_id)
            
            fs.delete(file_id)
            logging.info(f"✅ File deleted successfully: {file_id}")
        except Exception as e:
            logging.error(f"❌ Failed to delete file {file_id}: {e}")
            raise
    
    def validate_object_id(self, id_string):
        """
        Validate ObjectId format
        
        Args:
            id_string (str): String to validate as ObjectId
            
        Returns:
            ObjectId: Valid ObjectId
            
        Raises:
            ValueError: If the string is not a valid ObjectId
        """
        try:
            return ObjectId(id_string)
        except (InvalidId, TypeError):
            raise ValueError(f"Invalid ObjectId format: {id_string}")
    
    def get_file_by_metadata(self, metadata_query):
        """
        Get files by metadata query
        
        Args:
            metadata_query (dict): Query for metadata fields
            
        Returns:
            list: List of files matching metadata criteria
        """
        try:
            fs, db = self._get_connection()
            query = {"metadata": metadata_query}
            files = list(fs.find(query))
            logging.info(f"✅ Found {len(files)} files by metadata query")
            return files
        except Exception as e:
            logging.error(f"❌ Failed to find files by metadata: {e}")
            raise
    
    def file_exists(self, file_id):
        """
        Check if a file exists in GridFS
        
        Args:
            file_id (str or ObjectId): ID of the file to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            fs, db = self._get_connection()
            file_id = self.validate_object_id(file_id)
            
            file_info = fs.find_one({'_id': file_id})
            return file_info is not None
        except Exception as e:
            logging.error(f"❌ Failed to check file existence {file_id}: {e}")
            return False
    
    def get_file_size(self, file_id):
        """
        Get the size of a file in GridFS
        
        Args:
            file_id (str or ObjectId): ID of the file
            
        Returns:
            int: File size in bytes
        """
        try:
            file_info = self.get_file_info(file_id)
            return file_info.length
        except Exception as e:
            logging.error(f"❌ Failed to get file size {file_id}: {e}")
            raise
    
    def list_all_files(self, limit=None):
        """
        List all files in GridFS
        
        Args:
            limit (int): Optional limit on number of files to return
            
        Returns:
            list: List of all file documents
        """
        try:
            fs, db = self._get_connection()
            query = {}
            files = list(fs.find(query).limit(limit) if limit else fs.find(query))
            logging.info(f"✅ Listed {len(files)} files")
            return files
        except Exception as e:
            logging.error(f"❌ Failed to list files: {e}")
            raise

# Global service instance
gridfs_service = GridFSService()
