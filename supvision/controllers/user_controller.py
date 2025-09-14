from flask import request, jsonify, current_app, send_file
from models.user_model import User, Role
from utils.validation_utils import (
    generate_secure_encryption_key,
    sanitize_input,
)
from mongoengine.errors import ValidationError, NotUniqueError
from bson import ObjectId
import io

# --- CREATE ---
def create_user():
    """Create a new user with comprehensive validation"""
    data = request.json or {}

    # Required field validation
    required_fields = ['name', 'email','faculty_id', 'password', 'phone', 'role', 'department']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'error': f"{missing_fields} required fields",
        }), 400
    
    # Validate role
    if data.get('role') not in ['a', 'f']:
        return jsonify({
            'error': 'Invalid role. Must be "a" for admin or "f" for faculty'
        }), 400
    
    # Validate faculty_id is provided for faculty role
    if data.get('role') == 'f' and not data.get('faculty_id'):
        return jsonify({
            'error': 'faculty_id is required for faculty role'
        }), 400
    
    try:
        # Generate secure API key
        encryption_key = generate_secure_encryption_key()
        
        # Convert role string to enum
        role_enum = Role.ADMIN if data['role'] == 'a' else Role.FACULTY
        
        # Create user with validation
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=data['password'],  # Will be hashed automatically
            key=encryption_key,
            faculty_id=data.get('faculty_id'),
            department=data.get('department'),
            role=role_enum,
        )
        
        # Save user (validation happens in clean() method)
        user.save()
        
        return jsonify({
            'data': {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'faculty_id': user.faculty_id,
                'department': user.department,
                'role': user.role.value,
                'encryption_key': encryption_key,
            },
            'message': 'User created successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except NotUniqueError as e:
        # Check which field caused the uniqueness error
        if 'email' in str(e).lower():
            return jsonify({'error': 'Email already exists'}), 409
        elif 'phone' in str(e).lower():
            return jsonify({'error': 'Phone number already exists'}), 409
        elif 'faculty_id' in str(e).lower():
            return jsonify({'error': 'Faculty ID already exists'}), 409
        else:
            return jsonify({'error': 'Duplicate entry'}), 409
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'detail': str(e)
        }), 500

def login_user():
    """Login user with proper validation"""
    data = request.json or {}
    
    if not data.get('email') and not data.get('phone'):
        return jsonify({
            'error': 'Email or phone is required'
        }), 400
    elif not data.get('password'):
        return jsonify({
            'error': 'Password is required'
        }), 400

    query = {"email": data.get('email')} if data.get('email') else {"phone": data.get('phone')}

    try:
        # When we use ** before a dictionary (e.g., **query), it unpacks the dictionary into keyword arguments.
        # For example, if query = {'email': 'foo@bar.com'}, then User.objects.get(**query) is equivalent to User.objects.get(email='foo@bar.com').
        user = User.objects.get(**query)
        
        # Check password using the model method
        if user.check_password(data['password']):
            return jsonify({
                "message": 'Login successful',
                'user_id': str(user.id),
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'faculty_id': user.faculty_id,
                'department': user.department,
                'role': user.role.value,
            }), 200
        else:
            return jsonify({
                "error": "Invalid email or password"
            }), 401
        
    except User.DoesNotExist:
        return jsonify({
            "error": "Invalid email or password"
        }), 401
        
    except Exception as e:
        return jsonify({
            "error": "Login failed",
            "detail": str(e)
        }), 500

# --- READ ALL ---
def get_all_users():
    """Get all users with proper data formatting"""
    try:
        users = User.objects()
        output = []
        
        for user in users:
            output.append(user.to_dict())
        
        return jsonify({
            'users': output,
            'count': len(output)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve users',
            'detail': str(e)
        }), 500

# --- READ ONE ---
def get_user(user_id):
    """Get user by ID with proper error handling"""
    try:
        user = User.objects.get(id=user_id)
        return jsonify(user.to_dict()), 200
        
    except User.DoesNotExist:
        return jsonify({
            "error": "User not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve user',
            'detail': str(e)
        }), 500

# --- UPDATE ---
def update_user(user_id):
    """Update user with validation"""
    data = request.get_json() or {}
    
    if not data:
        return jsonify({
            'error': 'No data provided for update'
        }), 400
    
    # Validate role if provided
    if 'role' in data and data['role'] not in ['a', 'f']:
        return jsonify({
            'error': 'Invalid role. Must be "a" for admin or "f" for faculty'
        }), 400
    
    # Validate faculty_id requirement for faculty role
    if data.get('role') == 'f' and not data.get('faculty_id'):
        return jsonify({
            'error': 'faculty_id is required for faculty role'
        }), 400
    
    try:
        user = User.objects.get(id=user_id)
        
        # Update allowed fields
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'name' in data:
            user.name = data['name']
        if 'faculty_id' in data:
            user.faculty_id = data['faculty_id']
        if 'department' in data:
            user.department = data['department']
        if 'role' in data:
            user.role = Role.ADMIN if data['role'] == 'a' else Role.FACULTY
        
        # Save to trigger validation
        user.save()
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
        
    except User.DoesNotExist:
        return jsonify({
            "error": "User not found"
        }), 404
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except NotUniqueError as e:
        if 'email' in str(e).lower():
            return jsonify({'error': 'Email already exists'}), 409
        elif 'phone' in str(e).lower():
            return jsonify({'error': 'Phone number already exists'}), 409
        else:
            return jsonify({'error': 'Duplicate entry'}), 409
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update user',
            'detail': str(e)
        }), 500

# --- DELETE ---
def delete_user(user_id):
    """Delete user with proper error handling"""
    data = request.json or {}
    
    if not data.get('password'):
        return jsonify({
            'error': 'Password is required'
        }), 400
    
    try:
        user = User.objects.get(id=user_id)
        
        if user.check_password(data['password']):
            user.delete()
            return jsonify({"message": "The account has been deleted successfully"}), 200
        else:
            return jsonify({
                "error": "Invalid password"
            }), 401
        
    except User.DoesNotExist:
        return jsonify({
            "error": "User not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'detail': str(e),
            'error': 'Failed to delete user'
        }), 500

# --- ROLE-BASED OPERATIONS ---
def get_users_by_role(role):
    """Get all users by role"""
    try:
        # Validate role
        if role not in ['a', 'f']:
            return jsonify({
                'error': 'Invalid role. Must be "a" for admin or "f" for faculty'
            }), 400
        
        role_enum = Role.ADMIN if role == 'a' else Role.FACULTY
        users = User.objects(role=role_enum)
        
        output = []
        for user in users:
            output.append(user.to_dict())
        
        return jsonify({
            'users': output,
            'count': len(output),
            'role': role
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve users by role',
            'detail': str(e)
        }), 500

def get_faculty_by_id(faculty_id):
    """Get faculty user by faculty_id"""
    try:
        user = User.objects.get(faculty_id=faculty_id, role=Role.FACULTY)
        return jsonify(user.to_dict()), 200
        
    except User.DoesNotExist:
        return jsonify({
            "error": "Faculty not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve faculty',
            'detail': str(e)
        }), 500

def update_user_role(user_id):
    """Update only the role of a user (admin operation)"""
    data = request.get_json() or {}
    
    if 'role' not in data:
        return jsonify({
            'error': 'Role is required'
        }), 400
    
    if data['role'] not in ['a', 'f']:
        return jsonify({
            'error': 'Invalid role. Must be "a" for admin or "f" for faculty'
        }), 400
    
    # Validate faculty_id requirement for faculty role
    if data['role'] == 'f' and not data.get('faculty_id'):
        return jsonify({
            'error': 'faculty_id is required for faculty role'
        }), 400
    
    try:
        user = User.objects.get(id=user_id)
        
        # Update role
        user.role = Role.ADMIN if data['role'] == 'a' else Role.FACULTY
        
        # Update faculty_id if provided and role is faculty
        if data['role'] == 'f' and 'faculty_id' in data:
            user.faculty_id = data['faculty_id']
        elif data['role'] == 'a':
            # Clear faculty_id for admin role
            user.faculty_id = None
        
        user.save()
        
        return jsonify({
            "message": "User role updated successfully",
            "user": user.to_dict()
        }), 200
        
    except User.DoesNotExist:
        return jsonify({
            "error": "User not found"
        }), 404
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update user role',
            'detail': str(e)
        }), 500
