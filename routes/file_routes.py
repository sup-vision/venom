from flask import Blueprint, request, jsonify, send_file, current_app
from bson import ObjectId
import io

bp = Blueprint("file_routes", __name__)

@bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_id = current_app.fs.put(file, filename=file.filename)
    return jsonify({"message": "File uploaded", "file_id": str(file_id)})

@bp.route("/get/<file_id>", methods=["GET"])
def get_file(file_id):
    try:
        file = current_app.fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(file.read()), mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 404
