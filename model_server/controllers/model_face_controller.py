from flask import Blueprint, request, jsonify, current_app as app
from bson import ObjectId
from utils.face_utils import validate_face
from db import students_collection, mongodb_available
from services.gridfs_service import gridfs_service

face_bp = Blueprint("face_bp", __name__)
UPLOAD_FOLDER = "uploads"

def get_all_students(filterParams=None):
    """Get all students with optional filtering"""
    data = filterParams
    try:
        # Define fields that can be used for filtering students
        FINDABLE_FIELDS = [
            'name', 'roll_number', 'email', 'phone', 'section', 
            'semester', 'batch', 'course', 'branch'
        ]
        
        # If no data is provided, return all students
        if not data:
            students = list(students_collection.find({}))
        else:
            # Validate and filter data based on FINDABLE_FIELDS only
            # Extract only the fields that are in FINDABLE_FIELDS, ignoring any extra fields
            filter_query = {field: data[field] for field in FINDABLE_FIELDS if field in data}
            
            # If we have valid filter fields, use them for querying
            if len(filter_query) > 0:
                students = list(students_collection.find(filter_query))
            else:
                # If no valid filter fields found, return all students
                students = list(students_collection.find({}))

        output = [{
            'id': str(student['_id']),
            'name': student.get('name'),
            'roll_number': student.get('roll_number'),
            'email': student.get('email'),
            'phone': student.get('phone'),
            'section': student.get('section'),
            'semester': student.get('semester'),
            'batch': student.get('batch'),
            'course': student.get('course'),
            'branch': student.get('branch'),
            'face_id': student.get('face_id'),
            'sub_attendance': student.get('sub_attendance'),
            'created_at': student.get('created_at').isoformat() if student.get('created_at') else None
        } for student in students]

        return jsonify({'students': output, 'count': len(output)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve students', 'detail': str(e)}), 500

def register_face():
    if not mongodb_available:
        return jsonify({"error": "Database not available"}), 503
        
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    # Get student_id from form data (for file uploads)

    data = request.get_json()
    student_id = data.get("student_id")
    file_id = data.get("file_id")

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    # Check if student exists in database
    try:
        try:
            student = students_collection.find_one({"_id": ObjectId(student_id)})
            if not student:
                return jsonify({"error": "Student not found"}), 404
        except Exception as e:
            return jsonify({"error": "Invalid student_id format"}), 400

        file = None
        if file_id:
            try:
                file_id_obj = gridfs_service.validate_object_id(file_id)
            except ValueError as e:
                return jsonify({
                    'error': str(e)
                }), 400
            
            # Get file info
            file_info = gridfs_service.get_file_info(file_id_obj)
            if not file_info:
                return jsonify({
                    'error': 'Image not found'
                }), 404
            
            # Get file data
            file = gridfs_service.get_file(file_id_obj)
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve image',
            'detail': str(e)
        }), 500

    try:
        result = validate_face(file, ObjectId(student_id))
        
        # Update student record with face registration status
        if result.get("success"):
            students_collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": {"face_registered": True, "last_face_update": result.get("timestamp")}}
            )
            result["student_info"] = {
                "name": student.get("name"),
                "roll_number": student.get("roll_number")
            }
        
        return jsonify(result), 200

    except Exception as e:
        app.logger.error(f"Error in register_face: {e}")
        return jsonify({"error": str(e)}), 500
