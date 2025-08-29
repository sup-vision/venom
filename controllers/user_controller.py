from flask import request, jsonify, current_app, send_file
from models.user_model import User
from utils.validation_utils import (
    generate_secure_api_key,
    validate_api_key_format,
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
    required_fields = ['email', 'password', 'phone', 'first_name', 'last_name']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'missing_fields': missing_fields
        }), 400
    
    try:
        # Generate secure API key
        api_key = generate_secure_api_key()
        
        # Create user with validation
        user = User(
            email=data['email'],
            phone=data['phone'],
            password_hash=data['password'],  # Will be hashed automatically
            key=api_key,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )
        
        # Save user (validation happens in clean() method)
        user.save()
        
        return jsonify({
            'data': {
                'id': str(user.id),
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'api_key': api_key,
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
        else:
            return jsonify({'error': 'Duplicate entry'}), 409
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'detail': str(e)
        }), 500

def login_user(user_id):
    """Login user with proper validation"""
    data = request.json or {}
    
    if not data.get('email') or not data.get('password'):
        return jsonify({
            'error': 'Email and password are required'
        }), 400
    
    try:
        # Find user by email instead of user_id for login
        user = User.objects.get(email=data['email'])
        
        # Check password using the model method
        if user.check_password(data['password']):
            return jsonify({
                "message": 'Login successful',
                'user_id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
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
# def update_user(user_id):
#     """Update user with validation"""
#     data = request.get_json() or {}
    
#     if not data:
#         return jsonify({
#             'error': 'No data provided for update'
#         }), 400
    
#     try:
#         user = User.objects.get(id=user_id)
        
#         # Validate fields before update
#         update_data = {}
    
#         # Update user with validated data
#         if update_data:
#             user.update(**update_data)
        
#         # Save to trigger validation
#         user.save()
        
#         return jsonify({
#             "message": "User updated successfully",
#             "user": user.to_dict()
#         }), 200
        
#     except User.DoesNotExist:
#         return jsonify({
#             "error": "User not found"
#         }), 404
        
#     except ValidationError as e:
#         return jsonify({
#             'error': 'Validation error',
#             'details': str(e)
#         }), 400
        
#     except NotUniqueError as e:
#         if 'email' in str(e).lower():
#             return jsonify({'error': 'Email already exists'}), 409
#         elif 'phone' in str(e).lower():
#             return jsonify({'error': 'Phone number already exists'}), 409
#         else:
#             return jsonify({'error': 'Duplicate entry'}), 409
        
#     except Exception as e:
#         return jsonify({
#             'error': 'Failed to update user',
#             'detail': str(e)
#         }), 500

# --- DELETE ---
def delete_user(user_id):
    """Delete user with proper error handling"""
    data = request.json or {}
    if not data.get('password'):
        return jsonify({
            'error': 'Password is required'
        }), 400
    
    try:
        
        if user.check_password(data['password']):
            user = User.objects.get(id=user_id)
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
            'error': 'Failed to delete user',
            'detail': str(e)
        }), 500
