from flask import Blueprint
from controllers.image_controller import (
    upload_image,
    get_image,
    get_image_metadata,
    get_images_by_user,
    delete_image,
    get_image_base64
)

# Create blueprint for image routes
bp = Blueprint('image', __name__)

# --- IMAGE UPLOAD ROUTES ---

@bp.route('/upload', methods=['POST'])
def upload_image_route():
    """Upload single or multiple images to GridFS with associated_id metadata"""
    return upload_image()

# --- IMAGE RETRIEVAL ROUTES ---

@bp.route('/<file_id>', methods=['GET'])
def get_image_route(file_id):
    """Get an image by file_id (returns actual image file)"""
    return get_image(file_id)

@bp.route('/<file_id>/metadata', methods=['GET'])
def get_image_metadata_route(file_id):
    """Get image metadata without downloading the actual image"""
    return get_image_metadata(file_id)

@bp.route('/<file_id>/base64', methods=['GET'])
def get_image_base64_route(file_id):
    """Get image as base64 encoded string"""
    return get_image_base64(file_id)

# --- IMAGE QUERY ROUTES ---

@bp.route('/associated/<id>', methods=['GET'])
def get_images_by_user_route(id):
    """Get all images for a specific associated_id"""
    return get_images_by_user(id)

# --- IMAGE MANAGEMENT ROUTES ---

@bp.route('/<file_id>', methods=['DELETE'])
def delete_image_route(file_id):
    """Delete an image from GridFS"""
    return delete_image(file_id)
