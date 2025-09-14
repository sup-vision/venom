import os
import logging
from flask import request, jsonify
from face_recognition.engine import process_image, ensure_initialized
from db import students_collection, files_collection
from services.gridfs_service import gridfs_service
from datetime import datetime
import tempfile
from bson import ObjectId

def build_attendance_response(recognized_students, students):
    recognized_ids = {str(s['student_id']) for s in recognized_students}
    result_students, present_count = [], 0

    for student in students:
        sid = str(student["_id"])
        if sid in recognized_ids:
            recog_data = next((s for s in recognized_students if str(s['student_id']) == sid), {})
            result_students.append({
                "student_id": sid,
                "name": student.get("name"),
                "roll_number": student.get("roll_number"),
                "is_present": "present",
                "confidence": recog_data.get("confidence", None)
            })
            present_count += 1
        else:
            result_students.append({
                "student_id": sid,
                "name": student.get("name"),
                "roll_number": student.get("roll_number"),
                "is_present": "absent",
                "confidence": None
            })

    summary = {
        "total_students": len(students),
        "present": present_count,
        "absent": len(students) - present_count,
        "processed_at": datetime.now().isoformat(),
        "total_faces_detected": len(recognized_students)
    }

    return {"students": result_students, "recognition_summary": summary}

def fetch_class_images():
    """
    Given uploaded_file_ids in the request, fetch the corresponding images from GridFS
    and return them in the response (as base64-encoded strings).
    """
    import base64

    try:
        data = request.get_json()
        if not data or 'attendance_data' not in data:
            return jsonify({"error": "No attendance_data provided"}), 400

        attendance_data = data['attendance_data']
        uploaded_file_ids = attendance_data.get('uploaded_file_ids', [])

        if not uploaded_file_ids:
            return jsonify({"error": "No uploaded_file_ids provided"}), 400

        images = []
        for file_id in uploaded_file_ids:
            try:
                if gridfs_service.file_exists(file_id):
                    file_data = gridfs_service.get_file(file_id)
                    file_info = gridfs_service.get_file_info(file_id)
                    # Encode image data as base64 for JSON transport
                    encoded_data = base64.b64encode(file_data).decode('utf-8')
                    images.append({
                        "_id": file_id,
                        "filename": file_info.filename,
                        "metadata": file_info.metadata,
                        "image_base64": encoded_data
                    })
                else:
                    logging.warning(f"File with ID {file_id} not found in GridFS")
            except Exception as e:
                logging.error(f"Error retrieving file {file_id}: {e}")

        if not images:
            return jsonify({"error": "No valid files found"}), 404

        return images

    except Exception as e:
        logging.error(f"Error in fetch_class_images: {e}")
        return jsonify({"error": str(e)}), 500
        
def attendance_from_image():
    try:
        if not ensure_initialized():
            return jsonify({"error": "Face recognition system could not be initialized"}), 503

        if 'images' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_files = request.files.getlist('images')
        id = request.form.get('id')

        # This block saves the uploaded image file to a temporary file on disk,
        # so it can be processed by the face recognition system.
        recognized_students=[]
        for image_file in image_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                image_path = tmp.name
                image_file.save(image_path)
            try:
                # Get filter parameters from request if provided
                filter_params = {}
                if request.form.get('branch'):
                    filter_params['branch'] = request.form.get('branch')
                if request.form.get('section'):
                    filter_params['section'] = request.form.get('section')
                if request.form.get('semester'):
                    filter_params['semester'] = request.form.get('semester')
                
                # Process image with filter parameters - this will reinitialize the system with filtered students
                recognized_students.extend(process_image(image_path, filter_params))
                
                # Get students based on the same filter parameters for response
                if filter_params:
                    students = list(students_collection.find(filter_params, {"name": 1, "roll_number": 1}))
                else:
                    students = list(students_collection.find({}, {"name": 1, "roll_number": 1}))
            finally:
                os.remove(image_path)
        
        # Remove duplicates from recognized_students based on 'student_id'
        unique_students = {}
        for s in recognized_students:
            sid = str(s.get('student_id'))
            if sid not in unique_students:
                unique_students[sid] = True

        result = []
        for sid in unique_students.keys():
            result.append({
                "student_id": sid,
                "is_present": "p"
            })

        return jsonify(result)
        # response = build_attendance_response(recognized_students, students)
        # return jsonify(response)

    except Exception as e:
        logging.error(f"Error in attendance_from_image: {e}")
        return jsonify({"error": str(e)}), 500

def test_attendance():
    try:
        image_name = request.args.get("image")
        if not image_name:
            return jsonify({"error": "Please provide ?image=<filename> in query params"}), 400

        if not ensure_initialized():
            return jsonify({"error": "Face recognition system could not be initialized"}), 503

        base_dir = os.getenv("CLASS_IMAGE_DIR", "/Users/skakibahammed/code_playground/Recognition/datasets/crowds")
        image_path = os.path.join(base_dir, image_name)

        if not os.path.exists(image_path):
            return jsonify({"error": f"Image not found at {image_path}"}), 404

        # Get filter parameters from query params if provided
        filter_params = {}
        if request.args.get('branch'):
            filter_params['branch'] = request.args.get('branch')
        if request.args.get('section'):
            filter_params['section'] = request.args.get('section')
        if request.args.get('semester'):
            filter_params['semester'] = request.args.get('semester')
        
        # Process image with filter parameters - this will reinitialize the system with filtered students
        recognized_students = process_image(image_path, filter_params)
        
        # Get students based on the same filter parameters for response
        if filter_params:
            students = list(students_collection.find(filter_params, {"name": 1, "roll_number": 1}))
        else:
            students = list(students_collection.find({}, {"name": 1, "roll_number": 1}))
        
        response = build_attendance_response(recognized_students, students)

        return jsonify({"image": image_name, **response})

    except Exception as e:
        logging.error(f"Error in test_attendance: {e}")
        return jsonify({"error": str(e)}), 500
