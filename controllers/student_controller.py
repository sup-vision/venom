from flask import request, jsonify
from models.student_model import Student
from mongoengine.errors import ValidationError, NotUniqueError
from datetime import datetime
import re

# Define updatable fields for student
UPDATABLE_FIELDS = [
    'phone', 'email', 'name', 'section', 'semester', 
    'batch', 'course', 'branch', 'face_id', 'sub_attendance'
]
FINDABLE_FIELDS = [
    'section', 'semester', 'course', 'branch'
]
FINDABLE_FIELDS_WITH_ROLL_NUMBER = [
    'roll_number', 'section', 'semester', 
    'batch', 'course', 'branch'
]


# --- CREATE ---
def create_student():
    """
    Example of expected request data (JSON):

    For a single student:
    {
        "phone": "9876543210",
        "email": "student@example.com",
        "name": "John Doe",
        "roll_number": "CS2023001",
        "section": "A",
        "semester": "6",
        "batch": "2023",
        "course": "B.Tech",
        "branch": "CSE",
        "face_id": "faceid_123",
        "sub_attendance": [
            {
                "subject_code": "CS101",
                "attendance_percentage": 85
            },
            {
                "subject_code": "MA102",
                "attendance_percentage": 90
            }
        ]
    }

    For bulk create (list of students):
    [
        {
            "phone": "9876543210",
            "email": "student1@example.com",
            "name": "John Doe",
            "roll_number": "CS2023001",
            "section": "A",
            "semester": "6",
            "batch": "2023",
            "course": "B.Tech",
            "branch": "CSE",
            "face_id": "faceid_123",
            "sub_attendance": [
                {
                    "subject_code": "CS101",
                    "attendance_percentage": 85
                }
            ]
        },
        {
            "phone": "9876543211",
            "email": "student2@example.com",
            "name": "Jane Smith",
            "roll_number": "CS2023002",
            "section": "B",
            "semester": "6",
            "batch": "2023",
            "course": "B.Tech",
            "branch": "CSE",
            "face_id": "faceid_124",
            "sub_attendance": []
        }
    ]
    """
    data = request.json or {}

    # Required field validation
    required_fields = [
        'phone', 'email', 'name', 'roll_number', 'section', 
        'semester', 'batch', 'course', 'branch', 'sub_attendance'
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
                    sub_attendance=student['sub_attendance'],
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

# --- GET STUDENTS BY SUBJECT ---
def get_students_by_subject():
    """Get all students enrolled in a specific subject"""
    try:
        # Retrieve the 'subject_code' parameter from the query string of the request and remove any leading/trailing whitespace.
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