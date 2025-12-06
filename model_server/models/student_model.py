from mongoengine import (
    Document, StringField, DateTimeField, ListField, ObjectIdField, ValidationError
)
from datetime import datetime
import bcrypt
import re

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
    password_hash = StringField(required=False, min_length=8, max_length=128)
    face_id = ObjectIdField()
    face_embedding = StringField()
    sub_attendance = ListField(ObjectIdField())
    created_at = DateTimeField(default=datetime.utcnow)

    def clean(self):
        """Custom validation method called before saving"""
        self._validate_password_strength()

    def _validate_password_strength(self):
        """Validate password strength"""
        if not self.password_hash:
            return

        hashed_prefixes = ("$2a$", "$2b$", "$2y$")
        if self.password_hash.startswith(hashed_prefixes):
            return

        # Plain password needs to be validated and hashed
        password = self.password_hash
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        if len(password) > 128:
            raise ValidationError('Password must be no more than 128 characters long')

        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit')

        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def set_password(self, password):
        """Set password with automatic hashing"""
        if not password:
            raise ValidationError('Password cannot be empty')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        if len(password) > 128:
            raise ValidationError('Password must be no more than 128 characters long')

        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit')

        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if provided password matches the hash"""
        if not self.password_hash or not password:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False
