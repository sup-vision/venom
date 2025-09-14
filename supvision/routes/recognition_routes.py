from flask import Blueprint
from controllers.recognition_controller import (
    process_face_recognition,
    upload_student_images,
    get_recognition_status
)

# Create blueprint for recognition routes
bp = Blueprint('recognition', __name__)

# --- FACE RECOGNITION ROUTES ---

@bp.route('', methods=['POST'])
def process_face_recognition_route():
    """Process face recognition with class images and student embeddings"""
    return process_face_recognition()

@bp.route('/upload', methods=['POST'])
def upload_student_images_route():
    """Upload student images for face recognition"""
    return upload_student_images()

@bp.route('/status', methods=['GET'])
def get_recognition_status_route():
    """Get face recognition service status"""
    return get_recognition_status()
