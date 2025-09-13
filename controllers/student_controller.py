from flask import request, jsonify
from models.student_model import Student
from mongoengine.errors import ValidationError, NotUniqueError
from datetime import datetime
import re

# Define updatable fields for student
UPDATABLE_FIELDS = [
    'phone', 'email', 'name', 'roll_number', 'section', 'semester', 
    'batch', 'course', 'branch', 'face_id', 'face_embedding', 'sub_attendance'
]
FINDABLE_FIELDS = [
    'section', 'semester', 'branch', 'course'
]
FINDABLE_FIELDS_WITH_ROLL_NUMBER = [
    'roll_number', 'section', 'semester', 
    'batch', 'course', 'branch'
]


# --- CREATE ---
def create_student():
    data = request.json or {}

    # Required field validation
    required_fields = [
        'phone', 'email', 'name', 'roll_number', 'section', 
        'semester', 'batch', 'course', 'branch'
    ]
    # If data is a list (bulk create), check missing fields for each user
    missing_fields = []
    if isinstance(data, list):
        missing_fields = [field for field in required_fields if not data[0].get(field)]
    else:
        missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'missing_fields': missing_fields
        }), 400
    
    try:
        if isinstance(data, list):
            users = []
            for student in data:
                users.append(Student(
                    phone=student['phone'],
                    email=student['email'],
                    name=student['name'],
                    roll_number=student['roll_number'],
                    section=student['section'],
                    semester=student['semester'],
                    batch=student['batch'],
                    course=student['course'],
                    branch=student['branch'],
                    face_id=student.get('face_id'),
                    face_embedding=student.get('face_embedding'),
                    sub_attendance=student.get('sub_attendance', [])
                ))
                
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
                face_id=data.get('face_id'),
                face_embedding=data.get('face_embedding'),
                sub_attendance=data.get('sub_attendance', [])
            )
            students = [student]
        # Save students (validation happens in clean() method)
        students[0].save()
        
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

        return jsonify({
            'data': output,
            'message': 'Student created successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except NotUniqueError as e:
        # Check which field caused the uniqueness error
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
    data = request.get_json()
    try:
        # If no data is provided, return all students
        if not data:
            students = Student.objects()
        else:
            # Validate and filter data based on FINDABLE_FIELDS only
            # Extract only the fields that are in FINDABLE_FIELDS, ignoring any extra fields
            filter_query = {field: data[field] for field in FINDABLE_FIELDS if field in data}
            
            # If we have valid filter fields, use them for querying
            if len(filter_query) > 0:
                students = Student.objects(**filter_query)
            else:
                # If no valid filter fields found, return all students
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