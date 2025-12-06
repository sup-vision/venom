import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/venom')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1','true')
