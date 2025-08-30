# routes/user_routes.py
from flask import Blueprint
from controllers.user_controller import (
    create_user, 
    login_user,
    get_all_users,
    get_user,
    delete_user,
)

bp = Blueprint('user', __name__)

# Create user (simple example)
@bp.route('', methods=['POST'])
def create_user_route():
    return create_user()

@bp.route('/login', methods=['POST'])
def login_user_route():
    return login_user()

@bp.route('/all', methods=['GET'])
def get_all_users_route():
    return get_all_users()

@bp.route('/<user_id>', methods=['GET'])
def get_user_route(user_id):
    return get_user(user_id)

@bp.route('/<user_id>/delete', methods=['DELETE'])
def delete_user_route(user_id):
    return delete_user(user_id)