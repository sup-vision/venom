# routes/user_routes.py
from flask import Blueprint
from controllers.user_controller import (
    create_user, 
    upload_avatar, 
    get_avatar, 
    delete_avatar
)

bp = Blueprint('users', __name__)

# Create user (simple example)
@bp.route('', methods=['POST'])
def create_user_route():
    return create_user()

# Upload avatar
@bp.route('/<user_id>/avatar', methods=['POST'])
def upload_avatar_route(user_id):
    return upload_avatar(user_id)

# Get avatar
@bp.route('/<user_id>/avatar', methods=['GET'])
def get_avatar_route(user_id):
    return get_avatar(user_id)

# Delete avatar
@bp.route('/<user_id>/avatar', methods=['DELETE'])
def delete_avatar_route(user_id):
    return delete_avatar(user_id)
