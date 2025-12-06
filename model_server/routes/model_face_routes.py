from flask import Blueprint
from controllers.model_face_controller import register_face

face_bp = Blueprint("face_bp", __name__)
face_bp.route("/", methods=["POST"])(register_face)
