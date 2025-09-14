from flask import Blueprint, request, jsonify
from controllers.model_face_controller import register_face, get_student_info, list_students

face_bp = Blueprint("face_bp", __name__)

@face_bp.route("/", methods=["POST"])
def register_face_endpoint():
    return register_face()

@face_bp.route("/students", methods=["GET"])
def get_students():
    """Get list of all students"""
    students = list_students()
    return jsonify({"students": students, "count": len(students)})

@face_bp.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    """Get specific student information"""
    student = get_student_info(student_id)
    if student:
        return jsonify(student)
    else:
        return jsonify({"error": "Student not found"}), 404
