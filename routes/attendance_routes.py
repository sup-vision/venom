from flask import Blueprint, request
from controllers.attendance_controller import (
    create_attendance_bulk,
    update_attendance,
    get_attendance_by_student,
    get_attendance_by_subject
)

# Create blueprint for attendance routes
bp = Blueprint('attendance', __name__)

# --- ATTENDANCE ROUTES ---

# Create bulk attendance
@bp.route('/attendance/bulk', methods=['POST'])
def create_attendance_bulk_route():
    """Create attendance records for multiple students at once"""
    return create_attendance_bulk()

# Update single attendance
@bp.route('/attendance/<attendance_id>', methods=['PUT'])
def update_attendance_route(attendance_id):
    """Update a single attendance record"""
    return update_attendance(attendance_id)

# Get attendance by student
@bp.route('/attendance/student/<student_id>', methods=['GET'])
def get_attendance_by_student_route(student_id):
    """Get attendance records for a specific student"""
    # Get query parameters
    subject_id = request.args.get('subject_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    return get_attendance_by_student(student_id, subject_id, start_date, end_date)

# Get attendance by subject
@bp.route('/attendance/subject/<subject_id>', methods=['GET'])
def get_attendance_by_subject_route(subject_id):
    """Get attendance records for a specific subject"""
    # Get query parameters
    section = request.args.get('section')
    date = request.args.get('date')
    
    return get_attendance_by_subject(subject_id, section, date)
