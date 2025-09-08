from mongoengine import Document, StringField, DateTimeField, ListField, DictField, IntField, ObjectIdField
from datetime import datetime


# Put required for specific fields
class Student(Document):
    phone = StringField(required=True)
    email = StringField(required=True)
    name = StringField(required=True)
    roll_number = StringField(required=True) 
    section = StringField(required=True)
    semester = StringField(required=True)
    batch = StringField(required=True)
    course = StringField(required=True)
    branch = StringField(required=True)
    face_id = ObjectIdField()
    face_embedding = StringField(required=False)
    sub_attendance = ListField(ObjectIdField())
    created_at = DateTimeField(default=datetime.utcnow)