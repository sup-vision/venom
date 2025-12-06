import os
import logging
from flask import request, jsonify
from face_recognition.engine import process_image, ensure_initialized
from db import students_collection
from datetime import datetime
import tempfile
from bson import ObjectId
from bson.errors import InvalidId
from models.attendance_model import Attendance, IsPresent
from models.student_model import Student
from mongoengine import DoesNotExist, ValidationError
from datetime import datetime, timedelta, timezone

# Helper: get current IST datetime (timezone-aware)
def now_ist():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))

# Helper: convert a datetime (aware or naive) to IST (aware)
def to_ist(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume naive datetimes are in UTC, convert to IST
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone(timedelta(hours=5, minutes=30)))


def build_attendance(recognized_students, students, student_image_id, class_image_id, subject_name, subject_code, section, semester, branch):

    recognized_ids = {str(s['student_id']) for s in recognized_students}
    attendance_records = []
    errors = []
    
    # Validate ObjectId fields
    try:
        student_image_id_obj = ObjectId(student_image_id)
        class_image_id_obj = ObjectId(class_image_id)
    except (InvalidId, TypeError) as e:
        errors.append(f'Invalid ObjectId format for student_image_id or class_image_id: {str(e)}')
        return [], errors
    
    for i, student in enumerate(students):
        try:
            student_id = str(student["_id"])
            
            # Determine if student is present based on recognition
            is_present = IsPresent.PRESENT if student_id in recognized_ids else IsPresent.ABSENT
            
            # Get confidence if present
            confidence = None
            if is_present == IsPresent.PRESENT:
                recog_data = next((s for s in recognized_students if str(s['student_id']) == student_id), {})
                confidence = recog_data.get("confidence", None)
            
            # Build attendance record (created_at will be set automatically by the model)
            attendance_record = {
                "student_id": ObjectId(student_id),
                "student_image_id": student_image_id_obj,
                "class_image_id": class_image_id_obj,
                "subject_name": subject_name,
                "subject_code": subject_code,
                "is_present": is_present,
                "section": section,
                "semester": semester,
                "branch": branch
            }
            
            attendance_records.append(attendance_record)
            
        except (InvalidId, TypeError) as e:
            errors.append(f'Student {i+1}: Invalid ObjectId format - {str(e)}')
        except Exception as e:
            errors.append(f'Student {i+1}: {str(e)}')
    
    return attendance_records, errors


def create_attendance_bulk():
    try:
        if 'images' in request.files:
            image_files = request.files.getlist('images')
        elif 'image' in request.files:
            image_files = [request.files['image']]
        else:
            return jsonify({
                'error': 'Attendance bulk creation requires at least one image for recognition (keys: "images" or "image")'
            }), 400

        # Parse data
        if request.is_json:
            data = request.json or {}
        else:
            data = request.form.to_dict() or {}
            if 'data' in request.form:
                import json
                data = json.loads(request.form['data'])

        common_fields = ['subject_name', 'subject_code', 'section', 'semester', 'branch']
        for field in common_fields:
            if field not in data:
                return jsonify({
                    'error': f'{field} is required'
                }), 400

        if 'attendances' not in data or not isinstance(data['attendances'], list):
            return jsonify({
                'error': 'attendances array is required'
            }), 400

        if not data['attendances']:
            return jsonify({
                'error': 'attendances array cannot be empty'
            }), 400

        recognized_students = []
        image_paths = []
        class_image_ids = []

        if not ensure_initialized():
            return jsonify({
                "error": "Face recognition system could not be initialized"
            }), 503

        # Process all uploaded images
        try:
            for image_file in image_files:
                if not image_file or not getattr(image_file, 'filename', None):
                    continue
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    image_path = tmp.name
                    image_paths.append(image_path)
                    image_file.save(image_path)

            # Recognize students from all images (gather unique recognized)
            recognized_students_dict = {}
            for image_path in image_paths:
                try:
                    rec_students = process_image(image_path)
                    for rec in rec_students:
                        student_id_str = str(rec['student_id'])
                        if (student_id_str not in recognized_students_dict) or \
                           (rec.get('confidence', 0) > recognized_students_dict[student_id_str].get('confidence', 0)):
                            recognized_students_dict[student_id_str] = rec
                    class_image_ids.append(ObjectId())  # TODO: replace with actual image storage
                except Exception as e:
                    logging.warning(f"Error processing image {image_path}: {e}")

            recognized_students = list(recognized_students_dict.values())
            total_recognized = len(recognized_students)
        finally:
            for image_path in image_paths:
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        logging.warning(f"Failed to remove temp file: {e}")

        # If no students recognized, return an error
        if not recognized_students:
            return jsonify({
                'error': 'No students recognized in any of the provided images'
            }), 400

        recognized_ids = {str(s['student_id']) for s in recognized_students}

        # Get all students for section/semester/branch to validate
        all_students = Student.objects(
            section=data['section'],
            semester=data['semester'],
            branch=data['branch']
        )
        valid_student_ids = {str(s.id) for s in all_students}

        created_attendances = []
        errors = []


        # Process each attendance record (must be in recognized list)
        for i, attendance_data in enumerate(data['attendances']):
            try:
                # Validate student_id
                if 'student_id' not in attendance_data:
                    errors.append(f'Attendance {i+1}: student_id is required')
                    continue

                try:
                    student_id_obj = ObjectId(attendance_data['student_id'])
                except (InvalidId, TypeError):
                    errors.append(f'Attendance {i+1}: Invalid ObjectId format for student_id')
                    continue

                student_id_str = str(student_id_obj)
                # Must be recognized by image(s)
                if student_id_str not in recognized_ids:
                    errors.append(f'Attendance {i+1}: Student not recognized in any provided image')
                    continue

                # Validate student exists and belongs to the section/semester/branch
                if student_id_str not in valid_student_ids:
                    errors.append(f'Attendance {i+1}: Student not found in specified section/semester/branch')
                    continue

                try:
                    student = Student.objects.get(id=student_id_obj)
                except DoesNotExist:
                    errors.append(f'Attendance {i+1}: Student not found')
                    continue

                # Only allow present status for recognized students; absence must be due to absence from image
                is_present = IsPresent.PRESENT

                # For demo, pick the first class_image_id among the images (or leave None)
                class_image_id = class_image_ids[0] if class_image_ids else None

                # Create attendance record (only present for those found in image/recognized)
                # created_at will be automatically set by the model
                attendance = Attendance(
                    student_id=student_id_obj,
                    # student_image_id=student_image_id,
                    # class_image_id=class_image_id,
                    subject_name=data['subject_name'],
                    subject_code=data['subject_code'],
                    is_present=is_present,
                    section=data['section'],
                    semester=data['semester'],
                    branch=data['branch']
                )

                attendance.save()
                created_attendances.append(attendance.to_dict())

            except ValidationError as e:
                errors.append(f'Attendance {i+1}: {str(e)}')
            except Exception as e:
                errors.append(f'Attendance {i+1}: {str(e)}')
                logging.error(f"Error creating attendance {i+1}: {e}")

        # Build response
        response_data = {
            'message': 'Bulk attendance creation completed',
            'created_count': len(created_attendances),
            'total_attempted': len(data['attendances']),
            'recognized_count': len(recognized_students),
            'created_attendances': created_attendances
        }

        if errors:
            response_data['errors'] = errors
            response_data['error_count'] = len(errors)

        status_code = 201 if created_attendances else 400
        return jsonify(response_data), status_code

    except Exception as e:
        logging.error(f"Error in create_attendance_bulk: {e}")
        return jsonify({
            'error': 'Failed to create bulk attendance',
            'detail': str(e)
        }), 500


def attendance_from_image():
    try:
        if not ensure_initialized():
            return jsonify({"error": "Face recognition system could not be initialized"}), 503

        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image_path = tmp.name
            image_file.save(image_path)

        try:
            recognized_students = process_image(image_path)
            students = list(students_collection.find({}, {"name": 1, "roll_number": 1}))
            response = build_attendance(recognized_students, students)
            return jsonify(response)
        finally:
            os.remove(image_path)

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

        recognized_students = process_image(image_path)
        students = list(students_collection.find({}, {"name": 1, "roll_number": 1}))
        response = build_attendance(recognized_students, students)

        return jsonify({"image": image_name, **response})

    except Exception as e:
        logging.error(f"Error in test_attendance: {e}")
        return jsonify({"error": str(e)}), 500