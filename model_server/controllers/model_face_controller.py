import os, tempfile
from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.utils import secure_filename
from bson import ObjectId
from utils.face_utils import validate_face

face_bp = Blueprint("face_bp", __name__)
UPLOAD_FOLDER = "uploads"

def register_face():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    file = request.files["image"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(secure_filename(file.filename))[1]) as tmp:
        file.save(tmp.name)
        file_path = tmp.name

    try:
        result = validate_face(file_path, ObjectId(student_id))
        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error in register_face: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
