from flask import Blueprint, jsonify
from controllers.model_face_controller import register_face

face_bp = Blueprint("face_bp", __name__)

@face_bp.route("/", methods=["POST"])
def register_face_endpoint():
    return register_face()
