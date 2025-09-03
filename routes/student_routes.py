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
    update_attendance_for_subject
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

# --- SUBJECT-SPECIFIC ROUTES ---
@bp.route('/by-subject', methods=['GET'])
def get_students_by_subject_route():
    return get_students_by_subject()
