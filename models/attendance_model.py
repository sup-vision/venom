from mongoengine import Document, StringField, ObjectIdField, EnumField

class Is_present(Enum):
    PRESENT = 'p'
    ADSENT = 'a'

class Attendance(Document):
    student_id = ObjectIdField(required=True)
    subject_id = ObjectIdField(required=True)
    subject_code = StringField(required=True)
    ispresent = EnumField(Is_present, required=True, default=Role.ADSENT)
    section = StringField(required=True)
    semester = StringField(required=True)
    branch = StringField(required=True)