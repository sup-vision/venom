from flask import Blueprint
from controllers.model_attendance_controller import create_attendance_bulk

attendance_bp = Blueprint('attendance', __name__)

# @attendance_bp.route('/upload', methods=['POST'])
# def upload_image():
#   return attendance_from_image()

# @attendance_bp.route('/test', methods=['GET'])
# def test_image():
#   return test_attendance()

@attendance_bp.route('/bulk', methods=['POST'])
def bulk_attendance_route():
  return create_attendance_bulk()