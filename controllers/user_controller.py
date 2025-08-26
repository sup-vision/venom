from flask import request, jsonify
from models.user_model import User

# --- CREATE ---
def create_user():
    data = request.get_json()
    try:
        user = User(**data)
        user.save()
        return jsonify({"id": str(user.id)}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

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
            "age": user.age
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
