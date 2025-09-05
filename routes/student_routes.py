# routes/student_routes.py
from flask import Blueprint
from controllers.student_controller import (
    create_student,
    get_all_students,
    get_student,
    update_student,
    delete_student,
    search_students,
    get_students_by_subject,
    update_attendance_for_subject,
    add_face_embedding,  # Add this import
    get_face_embedding_status  # Add this import
)

bp = Blueprint('student', __name__)

@bp.route('', methods=['POST'])
def create_student_route():
    return create_student()

@bp.route('', methods=['GET'])
def get_all_students_route():
    return get_all_students()

@bp.route('/<student_id>', methods=['GET'])
def get_student_route(student_id):
    return get_student(student_id)

@bp.route('/<student_id>', methods=['PUT'])
def update_student_route(student_id):
    return update_student(student_id)

@bp.route('/<student_id>', methods=['DELETE'])
def delete_student_route(student_id):
    return delete_student(student_id)

# --- FACE EMBEDDING ROUTES ---
@bp.route('/<student_id>/face-embedding', methods=['POST'])
def add_face_embedding_route(student_id):
    return add_face_embedding(student_id)

@bp.route('/face-embedding-status', methods=['GET'])
def get_face_embedding_status_route():
    return get_face_embedding_status()

# --- SEARCH ROUTES ---
@bp.route('/search', methods=['GET'])
def search_students_route():
    return search_students()

# --- SUBJECT-SPECIFIC ROUTES ---
@bp.route('/by-subject', methods=['GET'])
def get_students_by_subject_route():
    return get_students_by_subject()

# --- ATTENDANCE ROUTES ---
@bp.route('/attendance/bulk-update', methods=['POST'])
def update_attendance_for_subject_route():
    return update_attendance_for_subject()