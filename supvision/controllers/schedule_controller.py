from flask import request, jsonify
from models.schedule_model import Schedule
from models.user_model import User, Role
from mongoengine.errors import ValidationError, DoesNotExist
from bson import ObjectId
from bson.errors import InvalidId

# --- CREATE ---
def create_schedule():
    """Create a new schedule with comprehensive validation"""
    data = request.json or {}

    # Required field validation (now includes 'day')
    required_fields = ['subject_code', 'subject_name', 'associative_fac_id', 'branch', 'section', 'semester', 'year', 'day', 'time']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'error': f"{missing_fields} required fields",
        }), 400
    
    # Validate faculty_id exists and is a faculty member
    try:
        faculty_id = ObjectId(data['associative_fac_id'])
        faculty = User.objects.get(id=faculty_id, role=Role.FACULTY)
    except (InvalidId, DoesNotExist):
        return jsonify({
            'error': 'Invalid faculty ID or faculty not found'
        }), 400
    
    try:
        # Create schedule with validation
        schedule = Schedule(
            subject_code=data['subject_code'],
            subject_name=data['subject_name'],
            associative_fac_id=faculty_id,
            branch=data['branch'],
            section=data['section'],
            semester=data['semester'],
            year=data['year'],
            day=data['day'],
            time=data['time'],
        )
        
        # Save schedule (validation happens in clean() method)
        schedule.save()
        
        return jsonify({
            'data': schedule.to_dict(),
            'message': 'Schedule created successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'detail': str(e)
        }), 500

# --- READ ALL ---
def get_all_schedules():
    """Get all schedules with proper data formatting"""
    try:
        schedules = Schedule.objects()
        output = []
        
        for schedule in schedules:
            output.append(schedule.to_dict())
        
        return jsonify({
            'schedules': output,
            'count': len(output)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve schedules',
            'detail': str(e)
        }), 500

# --- READ ONE ---
def get_schedule(schedule_id):
    """Get schedule by ID with proper error handling"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        return jsonify(schedule.to_dict()), 200
        
    except Schedule.DoesNotExist:
        return jsonify({
            "error": "Schedule not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve schedule',
            'detail': str(e)
        }), 500

# --- DELETE ---
def delete_schedule(schedule_id):
    """Delete schedule with proper error handling"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        schedule.delete()
        
        return jsonify({
            "message": "Schedule deleted successfully",
            "deleted_schedule": schedule.to_dict()
        }), 200
        
    except Schedule.DoesNotExist:
        return jsonify({
            "error": "Schedule not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete schedule',
            'detail': str(e)
        }), 500

# --- FACULTY-SPECIFIC OPERATIONS ---
def get_schedules_by_faculty(faculty_id):
    """Get all schedules for a specific faculty member"""
    try:
        # Validate faculty exists
        faculty = User.objects.get(id=faculty_id, role=Role.FACULTY)
        
        schedules = Schedule.objects(associative_fac_id=faculty_id)
        output = []
        
        for schedule in schedules:
            output.append(schedule.to_dict())
        
        return jsonify({
            'schedules': output,
            'count': len(output),
            'faculty_id': str(faculty_id)
        }), 200
        
    except User.DoesNotExist:
        return jsonify({
            "error": "Faculty not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve faculty schedules',
            'detail': str(e)
        }), 500

def get_schedules_by_branch_section(branch, section):
    """Get schedules by branch and section"""
    try:
        schedules = Schedule.objects(branch=branch, section=section)
        output = []
        
        for schedule in schedules:
            output.append(schedule.to_dict())
        
        return jsonify({
            'schedules': output,
            'count': len(output),
            'branch': branch,
            'section': section
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve schedules by branch and section',
            'detail': str(e)
        }), 500

def get_schedules_by_semester_year(semester, year):
    """Get schedules by semester and year"""
    try:
        schedules = Schedule.objects(semester=semester, year=year)
        output = []
        
        for schedule in schedules:
            output.append(schedule.to_dict())
        
        return jsonify({
            'schedules': output,
            'count': len(output),
            'semester': semester,
            'year': year
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve schedules by semester and year',
            'detail': str(e)
        }), 500

# --- UPDATE ---
def update_schedule(schedule_id):
    """Update schedule with validation"""
    data = request.get_json() or {}
    
    if not data:
        return jsonify({
            'error': 'No data provided for update'
        }), 400
    
    # Validate faculty_id if provided
    if 'associative_fac_id' in data:
        try:
            faculty_id = ObjectId(data['associative_fac_id'])
            faculty = User.objects.get(id=faculty_id, role=Role.FACULTY)
        except (InvalidId, DoesNotExist):
            return jsonify({
                'error': 'Invalid faculty ID or faculty not found'
            }), 400
    
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        
        # Update allowed fields
        if 'subject_code' in data:
            schedule.subject_code = data['subject_code']
        if 'subject_name' in data:
            schedule.subject_name = data['subject_name']
        if 'associative_fac_id' in data:
            schedule.associative_fac_id = ObjectId(data['associative_fac_id'])
        if 'branch' in data:
            schedule.branch = data['branch']
        if 'section' in data:
            schedule.section = data['section']
        if 'semester' in data:
            schedule.semester = data['semester']
        if 'year' in data:
            schedule.year = data['year']
        if 'day' in data:
            schedule.day = data['day']
        if 'time' in data:
            schedule.time = data['time']
        
        # Save to trigger validation
        schedule.save()
        
        return jsonify({
            "message": "Schedule updated successfully",
            "schedule": schedule.to_dict()
        }), 200
        
    except Schedule.DoesNotExist:
        return jsonify({
            "error": "Schedule not found"
        }), 404
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update schedule',
            'detail': str(e)
        }), 500
