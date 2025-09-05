#controllers/student_controller.py
from flask import request, jsonify
from models.student_model import Student
from mongoengine.errors import ValidationError, NotUniqueError
from datetime import datetime
import re
from utils.face_utils import extract_face_embedding

# Define updatable fields for student
UPDATABLE_FIELDS = [
    'phone', 'email', 'name', 'section', 'semester', 
    'batch', 'course', 'branch', 'face_id', 'sub_attendance'
]
FINDABLE_FIELDS = [
    'section', 'semester', 'branch', 'course'
]
FINDABLE_FIELDS_WITH_ROLL_NUMBER = [
    'roll_number', 'section', 'semester', 
    'batch', 'course', 'branch'
]


# --- CREATE --- (modified version)
def create_student():
    """
    Enhanced to support face image upload and embedding extraction.
    
    Now supports two ways of creating students:
    
    1. JSON-only (existing behavior):
        Content-Type: application/json
        Body: JSON with student data
    
    2. With image (new):
        Content-Type: multipart/form-data
        Form fields:
          - student_data: JSON string with student data
          - face_image: Image file containing student's face
    """
    # Check if request contains files (multipart form-data)
    if request.files:
        return create_student_with_image()
    else:
        return create_student_json_only()

def create_student_json_only():
    """Handle JSON-only student creation (existing functionality)"""
    data = request.json or {}
    return _create_student_internal(data, None)

def create_student_with_image():
    """Handle student creation with image upload"""
    try:
        # Get form data
        student_data_str = request.form.get('student_data')
        face_image = request.files.get('face_image')
        
        if not student_data_str:
            return jsonify({'error': 'student_data form field is required'}), 400
        
        if not face_image:
            return jsonify({'error': 'face_image file is required'}), 400
        
        # Parse student data
        import json
        try:
            data = json.loads(student_data_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in student_data'}), 400
        
        # Extract face embedding
        embedding, error = extract_face_embedding(face_image)
        if error:
            return jsonify({'error': f'Face processing failed: {error}'}), 400
        
        # Create student with embedding
        return _create_student_internal(data, embedding)
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

def _create_student_internal(data, face_embedding=None):
    """Internal method to create student with optional face embedding"""
    # Required field validation
    required_fields = [
        'phone', 'email', 'name', 'roll_number', 'section', 
        'semester', 'batch', 'course', 'branch', 'sub_attendance'
    ]
    
    missing_fields = []
    # Ensure data is parsed as JSON if it's a string
    if isinstance(data, str):
        import json
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format'}), 400

    if isinstance(data, list) and data:
        missing_fields = [field for field in required_fields if not data[0].get(field)]
    elif isinstance(data, dict):
        missing_fields = [field for field in required_fields if not data.get(field)]
    else:
        return jsonify({'error': 'Invalid data format. Expected a list or dictionary.'}), 400
    
    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'missing_fields': missing_fields
        }), 400
    
    try:
        if isinstance(data, list):
            users = []
            for student_data in data:
                student = Student(
                    phone=student_data['phone'],
                    email=student_data['email'],
                    name=student_data['name'],
                    roll_number=student_data['roll_number'],
                    section=student_data['section'],
                    semester=student_data['semester'],
                    batch=student_data['batch'],
                    course=student_data['course'],
                    branch=student_data['branch'],
                    sub_attendance=student_data['sub_attendance'],
                )
                if face_embedding:
                    student.face_embedding = face_embedding
                users.append(student)
                
            students = Student.objects.insert(users)
        else:
            student = Student(
                phone=data['phone'],
                email=data['email'],
                name=data['name'],
                roll_number=data['roll_number'],
                section=data['section'],
                semester=data['semester'],
                batch=data['batch'],
                course=data['course'],
                branch=data['branch'],
                sub_attendance=data.get('sub_attendance', [])
            )
            if face_embedding:
                student.face_embedding = face_embedding
            student.save()
            students = [student]
        
        output = [{
            'id': str(student.id),
            'name': student.name,
            'roll_number': student.roll_number,
            'email': student.email,
            'phone': student.phone,
            'section': student.section,
            'semester': student.semester,
            'batch': student.batch,
            'course': student.course,
            'branch': student.branch,
            'face_id': student.face_id,
            'has_face_embedding': student.face_embedding is not None,
            'sub_attendance': student.sub_attendance,
            'created_at': student.created_at.isoformat() if student.created_at else None
        } for student in students]

        return jsonify({
            'data': output,
            'message': 'Student created successfully' + 
                      (' with face embedding' if face_embedding else '')
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except NotUniqueError as e:
        if 'email' in str(e).lower():
            return jsonify({'error': 'Email already exists'}), 409
        elif 'phone' in str(e).lower():
            return jsonify({'error': 'Phone number already exists'}), 409
        elif 'roll_number' in str(e).lower():
            return jsonify({'error': 'Roll number already exists'}), 409
        else:
            return jsonify({'error': 'Duplicate entry'}), 409
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

# --- READ ALL ---
def get_all_students():
    data = request.get_json() or {}

    try:
        # If no data is provided, return all students
        if not data:
            students = Student.objects()
        # If all four filter fields are present and no extra fields, filter by them
        elif all(field in data for field in FINDABLE_FIELDS) and len(data) == len(FINDABLE_FIELDS):
            filter_query = {field: data[field] for field in FINDABLE_FIELDS}
            students = Student.objects(**filter_query)
        else:
            # If data is provided but not exactly the four filter fields, return all students
            students = Student.objects()

        output = [{
            'id': str(student.id),
            'name': student.name,
            'roll_number': student.roll_number,
            'email': student.email,
            'phone': student.phone,
            'section': student.section,
            'semester': student.semester,
            'batch': student.batch,
            'course': student.course,
            'branch': student.branch,
            'face_id': student.face_id,
            'sub_attendance': student.sub_attendance,
            'created_at': student.created_at.isoformat() if student.created_at else None
        } for student in students]

        return jsonify({'students': output, 'count': len(output)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve students', 'detail': str(e)}), 500

# --- READ ONE ---
def get_student(id):
    
    def is_valid_objectid(oid: str) -> bool:
        return bool(re.fullmatch(r"[0-9a-fA-F]{24}", oid))

    
    try:
        if is_valid_objectid(id):
            student = Student.objects.get(id=id)
        else:
            student = Student.objects.get(roll_number=id)
            
        return jsonify({
            'id': str(student.id),
            'name': student.name,
            'roll_number': student.roll_number,
            'email': student.email,
            'phone': student.phone,
            'section': student.section,
            'semester': student.semester,
            'batch': student.batch,
            'course': student.course,
            'branch': student.branch,
            'face_id': student.face_id,
            'sub_attendance': student.sub_attendance,
            'created_at': student.created_at.isoformat() if student.created_at else None
        }), 200
    except Student.DoesNotExist:
        return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve student', 'detail': str(e)}), 500

# --- UPDATE ---
def update_student(student_id):
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    try:
        student = Student.objects.get(id=student_id)
        
        # Check if all provided fields are in the updatable fields list
        invalid_fields = [field for field in data.keys() if field not in UPDATABLE_FIELDS]
        if invalid_fields:
            return jsonify({
                'error': 'Invalid fields provided',
                'invalid_fields': invalid_fields,
                'allowed_fields': UPDATABLE_FIELDS
            }), 400
        
        # Update allowed fields
        for field in UPDATABLE_FIELDS:
            if field in data:
                setattr(student, field, data[field])

        student.save()
        return jsonify({
            'message': 'Student updated successfully',
            'student': {
                'id': str(student.id),
                'name': student.name,
                'roll_number': student.roll_number,
                'updated_fields': list(data.keys())
            }
        }), 200

    except Student.DoesNotExist:
        return jsonify({'error': 'Student not found'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': str(e)}), 400
    except NotUniqueError as e:
        if 'email' in str(e).lower():
            return jsonify({'error': 'Email already exists'}), 409
        elif 'phone' in str(e).lower():
            return jsonify({'error': 'Phone number already exists'}), 409
        elif 'roll_number' in str(e).lower():
            return jsonify({'error': 'Roll number already exists'}), 409
        return jsonify({'error': 'Duplicate entry'}), 409
    except Exception as e:
        return jsonify({'error': 'Failed to update student', 'detail': str(e)}), 500

# --- BULK ATTENDANCE UPDATE ---
def update_attendance_for_subject():
    """
    Update attendance percentage for all students in a specific subject.

    Example of expected request data (JSON):

    {
        "subject_code": "CS101",
        "semester": "6",
        "section": "A",
        "branch": "CSE",
        "student_ids": [  # List of student IDs
            "665f2b1e2c8b4e1a2b3c4d5e",
            "665f2b1e2c8b4e1a2b3c4d5f"
        ]
    }
    """
    data = request.get_json() or {}
    

    # Validate required fields
    if 'subject_code' not in data:
        return jsonify({'error': 'subject_code is required'}), 400
    
    if 'student_ids' not in data:
        return jsonify({'error': 'student_ids is required'}), 400
    
    subject_code = data['subject_code']
    student_ids = data['student_ids']
    
    # Validate attendance_data format
    if not isinstance(student_ids, list):
        return jsonify({'error': 'attendance_data must be a list'}), 400
    
    try:
        all_students = []
        updated_count = 0
        errors = []

        missing_fields = [field for field in FINDABLE_FIELDS[:-1] if field not in data]
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
        else:
            filter_query = {field: data[field] for field in FINDABLE_FIELDS[:-1]}
            all_students = Student.objects(**filter_query)
        
        for student_id in student_ids:
            if student_id not in [str(student.id) for student in all_students]:
                errors.append(f"Student with ID {student_id} not found")
                continue  # Skip this ID and continue with the next one

            student = Student.objects.get(id=student_id)
            for i, sub_att in enumerate(student.sub_attendance):
                if sub_att.get('subject_code') == subject_code:
                    # Update attendance using your logic
                    attendance_percentage_old = student.sub_attendance[i]['attendance_percentage']
                    if attendance_percentage_old < 100:
                        total_classes = round(100 / (100 - attendance_percentage_old)) if attendance_percentage_old != 0 else 1
                        total_classes_attended = round((attendance_percentage_old / 100) * total_classes)
                        total_classes += 1
                        total_classes_attended += 1
                        new_percentage = (total_classes_attended / total_classes) * 100
                        student.sub_attendance[i]['attendance_percentage'] = new_percentage
                    else:
                        # Already 100%, just increment total_classes and attended
                        total_classes = 1
                        total_classes_attended = 1
                        student.sub_attendance[i]['attendance_percentage'] = 100
                    break
            else:
                student.sub_attendance.append({
                    'subject_code': subject_code,
                    'attendance_percentage': 0
                })
                
            student.save()
            updated_count += 1

        return jsonify({
            'message': f'Attendance update completed for subject {subject_code}',
            'updated_students': updated_count,
            'total_requests': len(student_ids),
            'errors': errors if errors else None,
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update attendance', 'detail': str(e)}), 500

# --- DELETE ---
def delete_student(student_id):
    """Delete a student"""
    try:
        student = Student.objects.get(id=student_id)
        student_name = student.name
        student.delete()
        return jsonify({'message': f'Student {student_name} deleted successfully'}), 200
    except Student.DoesNotExist:
        return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to delete student', 'detail': str(e)}), 500

# --- SEARCH STUDENTS ---
def search_students():
    """
    Search students by name, roll number, or email.
    The query expects a 'q' parameter in the request, which is used to search
    for students whose name, roll number, or email contains the search term (case-insensitive).
    Returns a list of matching students with their details.
    """
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400

        # The query expects to find students where the search term matches
        # any part of the name, roll number, or email (case-insensitive).
        students = Student.objects.filter(
            # The __raw__ argument allows you to pass a raw MongoDB query directly to MongoEngine.
            # Here, we use the $or operator to match if any of the fields (name, roll_number, or email)
            # contain the search term, case-insensitively.
            # The $regex operator is used to perform a regular expression search.
            # The "$options": "i" part makes the regex case-insensitive.
            # For example, {"name": {"$regex": search_term, "$options": "i"}} will match any student
            # whose name contains the search_term, regardless of case.
            __raw__={
                "$or": [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"roll_number": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}}
                ]
            }
        )

        output = [{
            'id': str(student.id),
            'name': student.name,
            'roll_number': student.roll_number,
            'email': student.email,
            'section': student.section,
            'semester': student.semester,
            'batch': student.batch,
            'course': student.course,
            'branch': student.branch
        } for student in students]

        return jsonify({
            'results': output,
            'count': len(output),
            'search_term': search_term
        }), 200
    except Exception as e:
        return jsonify({'error': 'Search failed', 'detail': str(e)}), 500

# --- GET STUDENTS BY SUBJECT ---
def get_students_by_subject():
    """Get all students enrolled in a specific subject"""
    try:
        subject_code = request.args.get('subject_code', '').strip()
        if not subject_code:
            return jsonify({'error': 'subject_code parameter is required'}), 400

        # Find students who have this subject in their sub_attendance
        students = Student.objects(sub_attendance__subject_code=subject_code)
        
        output = [{
            'id': str(student.id),
            'name': student.name,
            'roll_number': student.roll_number,
            'email': student.email,
            'section': student.section,
            'semester': student.semester,
            'batch': student.batch,
            'course': student.course,
            'branch': student.branch,
            'attendance_percentage': next(
                (att['attendance_percentage'] for att in student.sub_attendance 
                 if att.get('subject_code') == subject_code), None
            )
        } for student in students]

        return jsonify({
            'subject_code': subject_code,
            'students': output,
            'count': len(output)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve students by subject', 'detail': str(e)}), 500
    
# --- ADD FACE EMBEDDING TO EXISTING STUDENT ---    
def add_face_embedding(student_id):
    """Add face embedding to an existing student"""
    try:
        if 'face_image' not in request.files:
            return jsonify({'error': 'face_image file is required'}), 400
        
        face_image = request.files['face_image']
        if face_image.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get student
        student = Student.objects.get(id=student_id)
        
        # Extract face embedding
        embedding, error = extract_face_embedding(face_image)
        if error:
            return jsonify({'error': f'Face processing failed: {error}'}), 400
        
        # Update student with embedding
        student.face_embedding = embedding
        student.save()
        
        return jsonify({
            'message': 'Face embedding added successfully',
            'student_id': str(student.id),
            'name': student.name,
            'roll_number': student.roll_number
        }), 200
        
    except Student.DoesNotExist:
        return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

# --- GET FACE EMBEDDING STATUS ---
def get_face_embedding_status():
    """Get statistics about face embeddings"""
    try:
        total_students = Student.objects.count()
        students_with_embedding = Student.objects(face_embedding__exists=True).count()
        students_without_embedding = total_students - students_with_embedding
        
        return jsonify({
            'total_students': total_students,
            'students_with_embedding': students_with_embedding,
            'students_without_embedding': students_without_embedding,
            'coverage_percentage': round((students_with_embedding / total_students * 100), 2) if total_students > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get embedding status', 'detail': str(e)}), 500