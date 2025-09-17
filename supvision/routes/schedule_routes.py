from flask import Blueprint, jsonify
from controllers.schedule_controller import (
    create_schedule,
    get_all_schedules,
    get_schedule,
    delete_schedule,
    get_schedules_by_faculty,
    get_schedules_by_branch_section,
    get_schedules_by_semester_year,
    update_schedule
)

# Create blueprint for schedule routes
bp = Blueprint('schedule', __name__)

# --- SCHEDULE CRUD ROUTES ---

# Create schedule
@bp.route('', methods=['POST'])
def create_schedule_route():
    """Create a new schedule"""
    return create_schedule()

# Get all schedules
@bp.route('', methods=['GET'])
def get_all_schedules_route():
    """Get all schedules"""
    return get_all_schedules()

# Get schedule by ID
@bp.route('/<schedule_id>', methods=['GET'])
def get_schedule_route(schedule_id):
    """Get a specific schedule by ID"""
    return get_schedule(schedule_id)

# Update schedule
@bp.route('/<schedule_id>', methods=['PUT'])
def update_schedule_route(schedule_id):
    """Update a specific schedule by ID"""
    return update_schedule(schedule_id)

# Delete schedule
@bp.route('/<schedule_id>', methods=['DELETE'])
def delete_schedule_route(schedule_id):
    """Delete a specific schedule by ID"""
    return delete_schedule(schedule_id)

# --- FILTERED SCHEDULE ROUTES ---

# Get schedules by faculty
@bp.route('/faculty/<faculty_id>', methods=['GET'])
def get_schedules_by_faculty_route(faculty_id):
    """Get all schedules for a specific faculty member"""
    return get_schedules_by_faculty(faculty_id)

# Get schedules by branch and section
@bp.route('/branch/<branch>/section/<section>', methods=['GET'])
def get_schedules_by_branch_section_route(branch, section):
    """Get schedules by branch and section"""
    return get_schedules_by_branch_section(branch, section)

# Get schedules by semester and year
@bp.route('/semester/<semester>/year/<int:year>', methods=['GET'])
def get_schedules_by_semester_year_route(semester, year):
    """Get schedules by semester and year"""
    return get_schedules_by_semester_year(semester, year)

# --- QUERY PARAMETER ROUTES ---

# Get schedules with query parameters
@bp.route('/search', methods=['GET'])
def search_schedules_route():
    """Search schedules with query parameters"""
    from flask import request
    from models.schedule_model import Schedule
    
    try:
        # Get query parameters
        branch = request.args.get('branch')
        section = request.args.get('section')
        semester = request.args.get('semester')
        year = request.args.get('year', type=int)
        faculty_id = request.args.get('faculty_id')
        
        # Build query
        query = {}
        if branch:
            query['branch'] = branch
        if section:
            query['section'] = section
        if semester:
            query['semester'] = semester
        if year:
            query['year'] = year
        if faculty_id:
            from bson import ObjectId
            try:
                query['associative_fac_id'] = ObjectId(faculty_id)
            except:
                return jsonify({'error': 'Invalid faculty_id format'}), 400
        
        # Execute query
        schedules = Schedule.objects(**query)
        output = []
        
        for schedule in schedules:
            output.append(schedule.to_dict())
        
        return jsonify({
            'schedules': output,
            'count': len(output),
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to search schedules',
            'detail': str(e)
        }), 500
