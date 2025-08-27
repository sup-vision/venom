from mongoengine import Document, StringField, EmailField, DateTimeField
from datetime import datetime

class User(Document):
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    # store GridFS file id (ObjectId) as string
    avatar_file_id = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
