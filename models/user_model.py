from mongoengine import Document, StringField, EmailField, DateTimeField, ListField, ValidationError, ObjectIdField, ReferenceField, EnumField
from enum import Enum
from datetime import datetime
import re
import bcrypt

class Role(Enum):
    ADMIN = 'a'
    FACULTY = 'f'

class User(Document):
    # Email validation with proper format checking
    email = EmailField(required=True, unique=True, max_length=254)
    
    # Phone validation with E.164 format and uniqueness
    phone = StringField(required=True, unique=True, max_length=20)
    
    # Password validation with hash
    password_hash = StringField(required=True, min_length=8, max_length=128)
    
    # API key validation
    key = StringField(required=True)
    
    # Faculty ID field
    faculty_id = StringField(required=False, max_length=50)
    
    # Role field with enum validation
    role = EnumField(Role, required=True, default=Role.FACULTY)
    
    # 'searches' will store a list of Incident document references (ObjectIds)
    searches = ListField(ObjectIdField(), default=list)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Meta configuration
    meta = {
        'collection': 'user',
        'indexes': [
            'email',
            'key',
        ],
        'ordering': ['-created_at']
    }
    
    def clean(self):
        """Custom validation method called before saving"""
        self._validate_phone_format()
        self._validate_email_format()
        self._validate_password_strength()
        # self._validate_key_format()
        self._validate_searches()
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def _validate_phone_format(self):
        """Validate phone number is in E.164 format and only allows Indian country code (+91)"""
        if not self.phone:
            raise ValidationError('Phone number is required')
        
        # Only allow +91 followed by exactly 10 digits
        phone_pattern = r'^\+91\d{10}$'
        
        if not re.match(phone_pattern, self.phone):
            raise ValidationError(
                f'Phone number "{self.phone}" must be in E.164 format with Indian country code: +91XXXXXXXXXX'
            )
    
    def _validate_email_format(self):
        """Enhanced email validation"""
        if not self.email:
            raise ValidationError('Email is required')
        
        # Basic email format check (MongoEngine EmailField already does this)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, self.email):
            raise ValidationError(f'Invalid email format: {self.email}')
        
        # Check for common disposable email domains (optional)
        disposable_domains = [
            'tempmail.org', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'throwaway.email'
        ]
        
        domain = self.email.split('@')[-1].lower()
        if domain in disposable_domains:
            raise ValidationError(f'Disposable email domains are not allowed: {domain}')
    
    def _validate_password_strength(self):
        """Validate password strength"""
        if not self.password_hash:
            raise ValidationError('Password is required')
        
        # If this is a new password (not already hashed), validate strength
        if not  (
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
            has_upper = re.search(r'[A-Z]', password)
            has_lower = re.search(r'[a-z]', password)
            has_digit = re.search(r'\d', password)
            has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
            
            if not (has_upper and has_lower and has_digit):
                raise ValidationError(
                    'Password must contain at least one uppercase letter, one lowercase letter, and one digit'
                )
            
            # Hash the password
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _validate_searches(self):
        """Validate searches list (should be a list of ObjectId referencing IncidentModel)"""
        from bson import ObjectId

        if not isinstance(self.searches, list):
            raise ValidationError('Searches must be a list')

        validated_searches = []
        for incident_id in self.searches:
            if not isinstance(incident_id, ObjectId):
                # Try to convert from string to ObjectId
                try:
                    incident_id = ObjectId(incident_id)
                except Exception:
                    raise ValidationError(f'Invalid ObjectId in searches (should reference IncidentModel): {incident_id}')
            validated_searches.append(incident_id)

        self.searches = validated_searches
    
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
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive fields)"""
        return {
            'id': str(self.id),
            'email': self.email,
            'phone': self.phone,
            'faculty_id': self.faculty_id,
            'role': self.role.value if self.role else None,
            'searches': self.searches,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"User(email={self.email}, phone={self.phone}, role={self.role.value if self.role else None})"
    
    def __repr__(self):
        return f"<User: {self.email}, role={self.role.value if self.role else None}>"