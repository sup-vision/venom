# routes/user_routes.py
from flask import Blueprint
from controllers.user_controller import (
    create_user, 
    login_user,
    get_all_users,
    get_user,
    update_user,
    delete_user,
    get_users_by_role,
    get_faculty_by_id,
    update_user_role
)

bp = Blueprint('user', __name__)

# --- BASIC CRUD ROUTES ---

@bp.route('', methods=['POST'])
def create_user_route():
    """Create a new user"""
    return create_user()

@bp.route('/login', methods=['POST'])
def login_user_route():
    """Login user"""
    return login_user()

@bp.route('/all', methods=['GET'])
def get_all_users_route():
    """Get all users"""
    return get_all_users()

@bp.route('/<user_id>', methods=['GET'])
def get_user_route(user_id):
    """Get user by ID"""
    return get_user(user_id)

@bp.route('/<user_id>', methods=['PUT'])
def update_user_route(user_id):
    """Update user by ID"""
    return update_user(user_id)

@bp.route('/<user_id>/delete', methods=['DELETE'])
def delete_user_route(user_id):
    """Delete user by ID"""
    return delete_user(user_id)

# --- ROLE-BASED ROUTES ---

@bp.route('/role/<role>', methods=['GET'])
def get_users_by_role_route(role):
    """Get users by role (a for admin, f for faculty)"""
    return get_users_by_role(role)

@bp.route('/faculty/<faculty_id>', methods=['GET'])
def get_faculty_by_id_route(faculty_id):
    """Get faculty user by faculty_id"""
    return get_faculty_by_id(faculty_id)

@bp.route('/<user_id>/role', methods=['PUT'])
def update_user_role_route(user_id):
    """Update user role (admin operation)"""
    return update_user_role(user_id)