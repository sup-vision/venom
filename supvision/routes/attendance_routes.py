from flask import Blueprint, request
from controllers.attendance_controller import (
    create_attendance_bulk,
    update_attendance,
    get_attendance_by_student,
    # get_attendance_by_subject
)

# Create blueprint for attendance routes
bp = Blueprint('attendance', __name__)

# --- ATTENDANCE ROUTES ---

# Create bulk attendance
@bp.route('/bulk', methods=['POST'])
def create_attendance_bulk_route():
    """Create attendance records for multiple students at once"""
    return create_attendance_bulk()

# Update single attendance
@bp.route('/<attendance_id>', methods=['PUT'])
def update_attendance_route(attendance_id):
    """Update a single attendance record"""
    return update_attendance(attendance_id)

# Get attendance by student
@bp.route('/student/<student_id>', methods=['GET'])
def get_attendance_by_student_route(student_id):
    """Get attendance records for a specific student"""
    # Get query parameters
    subject_code = request.args.get('subject_code')
    return get_attendance_by_student(student_id, subject_code)

# Get attendance by subject
# @bp.route('/subject/<subject_code>', methods=['GET'])
# def get_attendance_by_subject_route(subject_code):
#     """Get attendance records for a specific subject"""
#     # Get query parameters
#     section = request.args.get('section')
#     return get_attendance_by_subject(subject_code, section)
