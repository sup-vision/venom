from mongoengine import Document, StringField, IntField, EmailField

class User(Document):
    name = StringField(required=True, max_length=50)
    email = EmailField(required=True, unique=True)
    age = IntField(min_value=0)

    meta = {"collection": "users"}
