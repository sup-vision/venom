from mongoengine import Document, StringField, DateTimeField, IntField, ListField, ObjectIdField
from datetime import datetime

class incident(Document):
    title = StringField(required=True)
    crowd_image_id = StringField(required=True)
    location = StringField(required=True)
    people_scanned = IntField(required=True)
    targets_found = ListField(ObjectIdField())
    created_at = DateTimeField(default=datetime.utcnow)