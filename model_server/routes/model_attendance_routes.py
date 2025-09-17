from flask import Blueprint, jsonify
from controllers.model_attendance_controller import attendance_from_image, test_attendance
from db import mongodb_available, students_collection

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/upload', methods=['POST'])
def upload_image():
  return attendance_from_image()

@attendance_bp.route('/test', methods=['GET'])
def test_image():
  return test_attendance()

@attendance_bp.route('/status', methods=['GET'])
def get_status():
  """Get database and system status"""
  try:
    student_count = students_collection.count_documents({}) if mongodb_available else 0
    return jsonify({
      "database_available": mongodb_available,
      "total_students": student_count,
      "status": "healthy" if mongodb_available else "unhealthy"
    })
  except Exception as e:
    return jsonify({
      "database_available": False,
      "total_students": 0,
      "status": "error",
      "error": str(e)
    }), 500
