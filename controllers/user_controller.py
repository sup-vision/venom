from flask import request, jsonify, current_app, send_file
from models.user_model import User
from bson import ObjectId
import io

# --- CREATE ---
def create_user():
    data = request.json or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error':'email & password required'}), 400
    # TODO: hash password before saving
    user = User(email=data['email'], password_hash=data['password']).save()
    return jsonify({'id': str(user.id), 'email': user.email}), 201

# --- READ ALL ---
def get_all_users():
    users = User.objects()
    output = []
    for u in users:
        output.append({
            "id":str(u.id),
            "name": u.name,
            "email": u.email,
            "age": u.age
        })
    return jsonify(output)

# --- READ ONE ---
def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        return jsonify({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "age": u.age
        })
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

# --- UPDATE ---
def update_user(user_id):
    data = request.get_json()
    try:
        user = User.objects.get(id=user_id)
        user.update(**data)
        return jsonify({"message": "User updated"})
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

# --- DELETE ---
def delete_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return jsonify({"message": "User deleted"})
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

# --- AVATAR OPERATIONS ---
def upload_avatar(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'error': 'user not found'}), 404

    if 'image' not in request.files:
        return jsonify({'error': 'no image file part'}), 400
    image = request.files['image']

    # Optionally validate file.mimetype

    # delete old avatar if exists
    if user.avatar_file_id:
        try:
            current_app.fs.delete(ObjectId(user.avatar_file_id))
        except Exception:
            pass

    # Save to GridFS. image.stream is file-like; GridFS.put accepts file-like or bytes
    file_id = current_app.fs.put(image.stream,
                                 filename=image.filename,
                                 contentType=image.mimetype,
                                 metadata={'user_id': ObjectId(user_id)})

    user.avatar_file_id = str(file_id)
    user.save()
    return jsonify({'file_id': str(file_id)}), 201

def get_avatar(user_id):
    user = User.objects(id=user_id).first()
    if not user or not user.avatar_file_id:
        return jsonify({'error': 'no avatar'}), 404

    try:
        grid_out = current_app.fs.get(ObjectId(user.avatar_file_id))
    except Exception:
        return jsonify({'error': 'file not found'}), 404

    # stream to client
    return send_file(io.BytesIO(grid_out.read()),
                     mimetype=getattr(grid_out, 'content_type', 'application/octet-stream'),
                     download_name=grid_out.filename)

def delete_avatar(user_id):
    user = User.objects(id=user_id).first()
    if not user or not user.avatar_file_id:
        return jsonify({'error': 'no avatar'}), 404

    try:
        current_app.fs.delete(ObjectId(user.avatar_file_id))
    except Exception as e:
        return jsonify({'error': 'delete failed', 'detail': str(e)}), 500

    user.avatar_file_id = None
    user.save()
    return jsonify({'status': 'deleted'}), 200
