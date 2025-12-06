import tempfile

MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
UPLOAD_FOLDER = tempfile.mkdtemp()
MONGO_URI = "mongodb://localhost:27017/venom"
DB_NAME = "attendance_system"
