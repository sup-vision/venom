from mongoengine import Document, StringField, DateTimeField, ListField, DictField, IntField, ObjectIdField, ValidationError
from datetime import datetime
import bcrypt
import re

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
            return  # Password is optional for students
        
        # If this is a new password (not already hashed), validate strength
        if not (
                self.password_hash.startswith("$2a$")
                or self.password_hash.startswith("$2b$")
                or self.password_hash.startswith("$2y$")
            ):
            # This is a plain password, validate before hashing
            password = self.password_hash
            
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long')
            
            if len(password) > 128:
                raise ValidationError('Password must be no more than 128 characters long')
            
            # Check for complexity requirements
            has_digit = re.search(r'\d', password)
            
            if not (has_digit):
                raise ValidationError(
                    'Password must contain at least one uppercase letter, one lowercase letter, and one digit'
                )
            
            # Hash the password
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def set_password(self, password):
        """Set password with automatic hashing"""
        if not password:
            raise ValidationError('Password cannot be empty')
        
        # Validate password strength
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if len(password) > 128:
            raise ValidationError('Password must be no more than 128 characters long')
        
        # Hash the password
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        if not self.password_hash or not password:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False