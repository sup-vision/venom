from mongoengine import Document, StringField, ObjectIdField, IntField, ValidationError, DateTimeField
from datetime import datetime
import re

class Schedule(Document):
    subject_code = StringField(required=True, max_length=20)
    subject_name = StringField(required=True, max_length=100)
    associative_fac_id = ObjectIdField(required=True)  # ObjectId of the teacher
    branch = StringField(required=True, max_length=50)
    section = StringField(required=True, max_length=10)
    semester = StringField(required=True, max_length=10)
    year = IntField(required=True)
    day = StringField(required=True, max_length=20)
    time = StringField(required=True, max_length=20)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Meta configuration
    meta = {
        'collection': 'schedule',
        'indexes': [
            'associative_fac_id',
            'branch',
            'section',
            'semester',
            'year',
        ],
        'ordering': ['-created_at']
    }
    
    def clean(self):
        """Custom validation method called before saving"""
        # self._validate_subject_code()
        self._validate_day_and_time()
        self._validate_semester()
        self._validate_year()
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    # def _validate_subject_code(self):
    #     """Validate subject code format"""
    #     if not self.subject_code:
    #         raise ValidationError('Subject code is required')
        
    #     # Subject code should be alphanumeric and follow a pattern
    #     if not re.match(r'^[A-Z]{2,3}\d{3,4}$', self.subject_code.upper()):
    #         raise ValidationError('Subject code must be in format like CS101, MAT201, etc.')
        
    #     self.subject_code = self.subject_code.upper()
    
    def _validate_day_and_time(self):
        """Validate day and time fields"""
        # Validate day
        if not hasattr(self, 'day') or not self.day:
            raise ValidationError('Day is required')
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if self.day.lower() not in valid_days:
            raise ValidationError('Day must be one of: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday')

        # Validate time (single time, e.g., 09:30 AM)
        if not self.time:
            raise ValidationError('Time is required')
        # Accept formats like "9:30 AM", "14:00", "2:15 pm"
        time_pattern = r'^([0-1]?\d|2[0-3]):[0-5]\d(\s?[APap][Mm])?$'
        if not re.match(time_pattern, self.time.strip()):
            raise ValidationError('Time must be in format HH:MM or HH:MM AM/PM (e.g., 09:30 AM, 14:00)')

    def _validate_semester(self):
        """Validate semester format"""
        if not self.semester:
            raise ValidationError('Semester is required')
        
        # Semester should be 1-8 or odd/even
        valid_semesters = ['1', '2', '3', '4', '5', '6', '7', '8', 'odd', 'even']
        if self.semester.lower() not in valid_semesters:
            raise ValidationError('Semester must be 1-8 or odd/even')
    
    def _validate_year(self):
        """Validate year is reasonable"""
        if not self.year:
            raise ValidationError('Year is required')
        
        current_year = datetime.now().year
        if self.year < 2020 or self.year > current_year + 5:
            raise ValidationError(f'Year must be between 2020 and {current_year + 5}')
    
    def to_dict(self):
        """Convert schedule to dictionary"""
        return {
            'id': str(self.id),
            'subject_code': self.subject_code,
            'subject_name': self.subject_name,
            'associative_fac_id': str(self.associative_fac_id),
            'branch': self.branch,
            'section': self.section,
            'semester': self.semester,
            'year': self.year,
            'time': self.time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"Schedule({self.subject_code} - {self.subject_name}, {self.branch} {self.section})"
    
    def __repr__(self):
        return f"<Schedule: {self.subject_code} - {self.subject_name}>"
