from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Target(Document):
    name = StringField(required=True)
    identity_number = StringField(required=True) # Adhaar, Voter ID, PAN Card, etc.
    blood_group = StringField(required=True)
    address = StringField(required=True)
    image_id = StringField(required=True)

    STATUS_CHOICES = ('wanted', 'convicted', 'released')
    status = StringField(required=True, choices=STATUS_CHOICES)
    
    created_at = DateTimeField(default=datetime.utcnow)