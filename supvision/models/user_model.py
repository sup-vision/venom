from mongoengine import Document, StringField, EmailField, DateTimeField, ValidationError, EnumField
from enum import Enum
from datetime import datetime
import re
import bcrypt

class Role(Enum):
    ADMIN = 'a'
    FACULTY = 'f'

class User(Document):
    name = StringField(required=True, max_length=50)
    email = EmailField(required=True, unique=True, max_length=254)
    phone = StringField(required=True, unique=True, max_length=20)
    password_hash = StringField(required=True, min_length=8, max_length=128)
    # Encryption key validation
    key = StringField(required=True)
    faculty_id = StringField(required=False, max_length=50, unique=True)
    department = StringField(required=False, max_length=50)
    role = EnumField(Role, required=True, default=Role.FACULTY)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Meta configuration
    meta = {
        'collection': 'user',
        'indexes': [
            'email',
            'phone',
            'faculty_id',
            'role'
        ],
        'ordering': ['-created_at']
    }
    
    def clean(self):
        """Custom validation method called before saving"""
        self._validate_name()
        self._validate_phone_format()
        self._validate_email_format()
        self._validate_password_strength()
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def _validate_name(self):
        """Validate name is present and meets requirements"""
        if not self.name or not self.name.strip():
            raise ValidationError('Name is required')
        if len(self.name) > 50:
            raise ValidationError('Name must be at most 50 characters long')
        # Optionally, add more name validation (e.g., no numbers/special chars)
    
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
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'faculty_id': self.faculty_id,
            'department': self.department,
            'role': self.role.value if self.role else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"User(name={self.name}, email={self.email}, phone={self.phone}, role={self.role.value if self.role else None})"
    
    def __repr__(self):
        return f"<User: {self.name}, email={self.email}, role={self.role.value if self.role else None}>"