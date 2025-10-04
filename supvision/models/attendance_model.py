from mongoengine import Document, StringField, ObjectIdField, EnumField, DateTimeField, ValidationError
from enum import Enum
from datetime import datetime

class IsPresent(Enum):
    PRESENT = 'p'
    ABSENT = 'a'

class Attendance(Document):
    student_id = ObjectIdField(required=True)
    # FIX: # 1. student_image_id and 2. class_image_id add this fields as required and production
    student_image_id = ObjectIdField()
    class_image_id = ObjectIdField()
    subject_name = StringField(required=True)
    subject_code = StringField(required=True)
    is_present = EnumField(IsPresent, required=True, default=IsPresent.ABSENT)
    section = StringField(required=True)
    semester = StringField(required=True)
    branch = StringField(required=True)
    date = DateTimeField(required=True, default=datetime.utcnow)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Meta configuration
    meta = {
        'collection': 'attendance',
        'indexes': [
            'student_id',
            'subject_code',
            'section',
            'semester',
            'branch',
            'date',
        ],
        'ordering': ['-created_at']
    }
    
    def clean(self):
        """Custom validation method called before saving"""
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert attendance to dictionary"""
        return {
            'id': str(self.id),
            'student_id': str(self.student_id),
            'student_image_id': str(self.student_image_id),
            'class_image_id': str(self.class_image_id),
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'is_present': self.is_present.value,
            'section': self.section,
            'semester': self.semester,
            'branch': self.branch,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"Attendance({self.subject_code} - {self.student_id} - {self.is_present.value})"
    
    def __repr__(self):
        return f"<Attendance: {self.subject_code} - {self.student_id}>"