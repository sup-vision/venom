# routes/student_routes.py
from flask import Blueprint
from controllers.student_controller import (
    create_student,
    get_all_students,
    get_student,
    update_student,
    delete_student,
    search_students
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

# --- SEARCH ROUTES ---
@bp.route('/search', methods=['GET'])
def search_students_route():
    return search_students()