from flask import request, jsonify
import json
from datetime import datetime, timedelta, timezone
from controllers.image_controller import upload_image
from controllers.student_controller import get_all_students

# Helper: get current IST datetime (timezone-aware)
def now_ist():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))

def process_face_recognition():
    """Process face recognition with class data and get students for the class"""
    try:
        # Get form data
        class_images = request.files.getlist('class_images')
        class_data = request.form.get('class_data')
        associated_id = request.form.get('id')  # For image upload
        
        if not class_images:
            return jsonify({
                'error': 'class_images are required'
            }), 400
        
        if not class_data:
            return jsonify({
                'error': 'class_data is required'
            }), 400
        
        try:
            class_data = json.loads(class_data)
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Invalid JSON format for class_data'
            }), 400

        branch = class_data.get('branch')
        section = class_data.get('section')
        semester = class_data.get('semester')
        subject_code = class_data.get('subject_code')
        subject_name = class_data.get('subject_name')

        if not all([branch, section, semester, subject_code, subject_name]):
            return jsonify({
                'error': 'branch, section, semester, subject_code, subject_name are required'
            }), 400
        
        if not associated_id:
            return jsonify({
                'error': 'associated_id is required for image storage'
            }), 400
        
        # Prepare filter parameters for get_all_students
        filter_params = {
            'branch': branch,
            'section': section,
            'semester': semester
        }
        
        try:
            students_response = get_all_students(filterParams=filter_params)
        except Exception as e:
            return jsonify({
                'error': 'Failed to get students',
                'detail': str(e)
            }), 500
        
        if students_response[1] != 200:
            return students_response
        
        students_data = students_response[0].get_json()
        students = students_data.get('students', [])
        
        try:
            images_response = upload_image({'images': class_images, 'id': associated_id})
        except Exception as e:
            return jsonify({
                'error': 'Failed to upload images',
                'detail': str(e)
            }), 500

        if images_response[1] != 201:
            return images_response
        
        images_data = images_response[0].get_json()
        uploaded_file_ids = [img['file_id'] for img in images_data.get('uploaded_images', [])]
        
        # Create attendance data structure similar to attendance.json
        attendance_data = {
            "subject_name": subject_name,
            "subject_code": subject_code,
            "section": section,
            "semester": semester,
            "branch": branch,
            "date": now_ist().isoformat(),
            "class_images": uploaded_file_ids,  # List of uploaded image IDs
            "attendances": []
        }
        
        # Process each student with proper structure
        for student in students:
            attendance_record = {
                "student_id": student["id"],
                "face_embeddings": student.get("face_embedding", []),  # Use existing face_embedding from student
                "is_present": "a"  # Default to absent, will be updated by model
            }
            attendance_data["attendances"].append(attendance_record)
        
        # Prepare response with image metadata information
        response_data = {
            "attendance_data": attendance_data,
            "image_metadata": {
                "uploaded_images": images_data.get('uploaded_images', []),
                "total_images": len(uploaded_file_ids),
                "upload_info": {
                    "message": images_data.get('message', ''),
                    "total_uploaded": images_data.get('total_uploaded', 0),
                    "total_attempted": images_data.get('total_attempted', 0)
                }
            },
            "class_info": {
                "subject_code": subject_code,
                "subject_name": subject_name,
                "branch": branch,
                "section": section,
                "semester": semester,
                "total_students": len(students)
            }
        }
        
        # Call dummy model server
        # model_response = call_model_server(attendance_data)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to process face recognition',
            'detail': str(e)
        }), 500

def upload_student_images():
    """Upload student images for face recognition"""
    try:
        # This function directly calls the image upload controller
        # It's a wrapper to maintain the recognition workflow
        return upload_image()
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to upload student images',
            'detail': str(e)
        }), 500

def get_recognition_status():
    """Get the status of face recognition processing"""
    try:
        # This could be used to check the status of ongoing recognition processes
        # For now, return a simple status
        return jsonify({
            'status': 'active',
            'message': 'Face recognition service is running',
            'timestamp': now_ist().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get recognition status',
            'detail': str(e)
        }), 500