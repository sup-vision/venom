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
    # List of dictionaries, each with 'subject_code' and 'attendance_percentage' (integer)
    sub_attendance = ListField(ObjectIdField())
        # DictField(
        #     fields={
        #         'subject_code': StringField(required=True),
        #         'attendance_percentage': IntField(min_value=0, max_value=100, default=0)
        #     }
        # ),
    created_at = DateTimeField(default=datetime.utcnow)