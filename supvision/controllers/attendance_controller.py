from flask import request, jsonify
from models.attendance_model import Attendance, IsPresent
from models.student_model import Student
from models.schedule_model import Schedule
from mongoengine.errors import ValidationError, DoesNotExist
from bson import ObjectId
from bson.errors import InvalidId
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

def create_attendance_bulk():
    """Create attendance records for multiple students at once.
    Date is automatically set to current time when teacher submits attendance."""
    data = request.json or {}
    
    # Validate required fields
    if 'attendances' not in data or not isinstance(data['attendances'], list):
        return jsonify({
            'error': 'attendances array is required'
        }), 400
    
    if not data['attendances']:
        return jsonify({
            'error': 'attendances array cannot be empty'
        }), 400
    
    # Validate common fields for all attendances
    # FIX: # 1. student_image_id and 2. class_image_id add this field and prod
    common_fields = ['subject_name', 'subject_code', 'section', 'semester', 'branch']
    for field in common_fields:
        if field not in data:
            return jsonify({
                'error': f'{field} is required for all attendances'
            }), 400
    
    # Set attendance date to current IST time when teacher submits
    attendance_date = now_ist()
    
    created_attendances = []
    errors = []
    
    try:
        for i, attendance_data in enumerate(data['attendances']):
            try:
                # Validate student exists
                if 'student_id' not in attendance_data:
                    errors.append(f'Attendance {i+1}: student_id is required')
                    continue
                
                # Validate ObjectId fields
                try:
                    student_id_obj = attendance_data['student_id']
                    # student_image_id_obj = ObjectId(data['student_image_id'])
                    # class_image_id_obj = ObjectId(data['class_image_id'])
                except (InvalidId, TypeError):
                    errors.append(f'Attendance {i+1}: Invalid ObjectId format for student_id, student_image_id, or class_image_id')
                    continue
                
                student = Student.objects.get(id=student_id_obj)
                
                # Validate attendance status
                is_present = attendance_data.get('is_present', 'a')
                if is_present not in ['p', 'a']:
                    errors.append(f'Attendance {i+1}: is_present must be "p" or "a"')
                    continue
                
                # Create attendance record
                attendance = Attendance(
                    student_id=student_id_obj,
                    # FIX: # 1. student_image_id and 2. class_image_id add this field and prod
                    # student_image_id=student_image_id_obj,
                    # class_image_id=class_image_id_obj,
                    subject_name=data['subject_name'],
                    subject_code=data['subject_code'],
                    is_present=IsPresent.PRESENT if is_present == 'p' else IsPresent.ABSENT,
                    section=data['section'],
                    semester=data['semester'],
                    branch=data['branch'],
                    date=attendance_date
                )
                
                attendance.save()
                created_attendances.append(attendance.to_dict())
                
            except (InvalidId, DoesNotExist) as e:
                errors.append(f'Attendance {i+1}: Student not found')
            except ValidationError as e:
                errors.append(f'Attendance {i+1}: {str(e)}')
            except Exception as e:
                errors.append(f'Attendance {i+1}: {str(e)}')
        
        response_data = {
            'message': f'Bulk attendance creation completed',
            'created_count': len(created_attendances),
            'total_attempted': len(data['attendances']),
            'created_attendances': created_attendances
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['error_count'] = len(errors)
        
        status_code = 201 if created_attendances else 400
        return jsonify(response_data), status_code
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create bulk attendance',
            'detail': str(e)
        }), 500

def update_attendance(attendance_id):
    """Update a single attendance record"""
    data = request.get_json() or {}
    
    if not data:
        return jsonify({
            'error': 'No data provided for update'
        }), 400
    
    # Validate is_present if provided
    if 'is_present' in data and data['is_present'] not in ['p', 'a']:
        return jsonify({
            'error': 'is_present must be "p" or "a"'
        }), 400
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        
        # Update allowed fields
        if 'is_present' in data:
            attendance.is_present = IsPresent.PRESENT if data['is_present'] == 'p' else IsPresent.ABSENT
        
        if 'date' in data:
            new_date = data['date']
            if isinstance(new_date, str):
                try:
                    # Parse as UTC, then convert to IST
                    new_date = datetime.fromisoformat(new_date.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'error': 'Invalid date format. Use ISO format'
                    }), 400
            
            # Ensure new_date is timezone-aware in IST
            new_date = to_ist(new_date)
            attendance.date = new_date
        
        # Save to trigger validation
        attendance.save()
        
        return jsonify({
            "message": "Attendance updated successfully",
            "attendance": attendance.to_dict()
        }), 200
        
    except Attendance.DoesNotExist:
        return jsonify({
            "error": "Attendance not found"
        }), 404
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update attendance',
            'detail': str(e)
        }), 500

def get_attendance_by_student(student_id, subject_code=None):
    """Get attendance records for a specific student with optional filters"""
    try:
        # Validate student exists
        student = Student.objects.get(id=student_id)
        # Build query
        query = {'student_id': student_id}
        
        if subject_code:
            query['subject_code'] = subject_code
        
        attendances = Attendance.objects.filter(**query)
        attendance_list = [attendance.to_dict() for attendance in attendances]
        
        # Calculate attendance statistics
        total_present = len([a for a in attendances if a.is_present.value == 'p'])
        total_absent = len([a for a in attendances if a.is_present.value == 'a'])
        total_classes = total_present + total_absent
        
        # Calculate subject-specific attendance
        subject_stats = {}
        for attendance in attendances:
            sub_code = attendance.subject_code
            if sub_code not in subject_stats:
                subject_stats[sub_code] = {
                    'subject_code': sub_code,
                    'subject_name': attendance.subject_name,
                    'present': 0,
                    'absent': 0,
                    'total': 0
                }
            
            if attendance.is_present.value == 'p':
                subject_stats[sub_code]['present'] += 1
            else:
                subject_stats[sub_code]['absent'] += 1
            subject_stats[sub_code]['total'] += 1
        
        # Calculate percentages for each subject
        for sub_code, stats in subject_stats.items():
            stats['attendance_percentage'] = round((stats['present'] / stats['total']) * 100, 2) if stats['total'] > 0 else 0
        
        # Calculate overall attendance percentage
        overall_percentage = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 0
        
        # Sort subject stats by subject_code
        sorted_subject_stats = sorted(subject_stats.values(), key=lambda x: x['subject_code'])
        
        response_data = {
            'count': len(attendance_list),
            'student_id': str(student_id),
            'attendance_summary': {
                'total_classes': total_classes,
                'total_present': total_present,
                'total_absent': total_absent,
                'overall_percentage': overall_percentage
            },
            'subject_statistics': sorted_subject_stats
        }
        
        return jsonify(response_data), 200
        
    except Student.DoesNotExist:
        return jsonify({
            "error": "Student not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve attendance',
            'detail': str(e)
        }), 500

# def get_attendance_by_subject(subject_code, section=None):
#     """Get attendance records for a specific subject with optional filters"""
#     try:
#         # Validate subject exists
#         subject = Schedule.objects.get(subject_code=subject_code)
        
#         # Build query
#         query = {'subject_code': subject_code}
        
#         if section:
#             query['section'] = section
        
#         attendances = Attendance.objects.get(**query)
#         output = []
        
#         for attendance in attendances:
#             output.append(attendance.to_dict())
        
#         return jsonify({
#             'attendances': output,
#             'count': len(output),
#             'subject_code': str(subject_code)
#         }), 200
        
#     except Schedule.DoesNotExist:
#         return jsonify({
#             "error": "Subject not found"
#         }), 404
        
#     except Exception as e:
#         return jsonify({
#             'error': 'Failed to retrieve attendance',
#             'detail': str(e)
#         }), 500
