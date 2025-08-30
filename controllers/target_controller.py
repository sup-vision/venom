from flask import request, jsonify
from models.target_model import Target
from mongoengine.errors import ValidationError, NotUniqueError
from datetime import datetime

# --- CREATE ---
def create_target():
    """Create a new criminal target for crowd surveillance system"""
    data = request.json or {}

    required_fields = ['name', 'identity_number', 'blood_group', 'address', 'image_id', 'status']
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({'error': 'Missing required fields', 'missing_fields': missing_fields}), 400

    try:
        target = Target(
            name=data['name'],
            identity_number=data['identity_number'],
            blood_group=data['blood_group'],
            address=data['address'],
            image_id=data['image_id'],
            status=data['status'],
            created_at=datetime.utcnow()
        )
        target.save()

        return jsonify({
            'data': {
                'id': str(target.id),
                'name': target.name,
                'identity_number': target.identity_number,
                'status': target.status,
                'image_id': target.image_id,
                'created_at': target.created_at.isoformat()
            },
            'message': 'Criminal target added to surveillance system successfully'
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': str(e)}), 400
    except NotUniqueError as e:
        if 'identity_number' in str(e).lower():
            return jsonify({'error': 'Identity number already exists'}), 409
        return jsonify({'error': 'Duplicate entry'}), 409
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

# --- READ ALL ---
def get_all_targets():
    """Get all criminal targets for surveillance monitoring"""
    try:
        targets = Target.objects()
        output = [{
            'id': str(target.id),
            'name': target.name,
            'identity_number': target.identity_number,
            'status': target.status,
            'blood_group': target.blood_group,
            'address': target.address,
            'image_id': target.image_id,
            'created_at': target.created_at.isoformat() if target.created_at else None
        } for target in targets]

        return jsonify({'targets': output, 'count': len(output)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve targets', 'detail': str(e)}), 500

# --- READ ONE ---
def get_target(target_id):
    """Get specific criminal target details for face recognition matching"""
    try:
        target = Target.objects.get(id=target_id)
        return jsonify({
            'id': str(target.id),
            'name': target.name,
            'identity_number': target.identity_number,
            'blood_group': target.blood_group,
            'address': target.address,
            'image_id': target.image_id,
            'status': target.status,
            'created_at': target.created_at.isoformat() if target.created_at else None
        }), 200
    except Target.DoesNotExist:
        return jsonify({'error': 'Target not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve target', 'detail': str(e)}), 500

# --- SEARCH ---
def search_targets():
    """Search criminals for crowd surveillance face matching"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400

        targets = Target.objects(name__icontains=search_term).union(
            Target.objects(identity_number__icontains=search_term)
        )

        output = [{
            'id': str(target.id),
            'name': target.name,
            'identity_number': target.identity_number,
            'status': target.status,
            'image_id': target.image_id
        } for target in targets]

        return jsonify({
            'results': output,
            'count': len(output),
            'search_term': search_term
        }), 200
    except Exception as e:
        return jsonify({'error': 'Search failed', 'detail': str(e)}), 500

# --- UPDATE ---
def update_target(target_id):
    """Update criminal target information"""
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    try:
        target = Target.objects.get(id=target_id)
        
        # Update allowed fields
        update_fields = ['identity_number', 'blood_group', 'address', 'image_id', 'status']
        for field in update_fields:
            if field in data:
                setattr(target, field, data[field])

        target.save()
        return jsonify({
            'message': 'Target updated successfully',
            'target': {'id': str(target.id), 'status': target.status}
        }), 200

    except Target.DoesNotExist:
        return jsonify({'error': 'Target not found'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': str(e)}), 400
    except NotUniqueError as e:
        if 'identity_number' in str(e).lower():
            return jsonify({'error': 'Identity number already exists'}), 409
        return jsonify({'error': 'Duplicate entry'}), 409
    except Exception as e:
        return jsonify({'error': 'Failed to update target', 'detail': str(e)}), 500

# --- UPDATE STATUS ---
def update_target_status(target_id):
    """Update criminal status when detected in surveillance"""
    data = request.get_json() or {}
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400

    try:
        target = Target.objects.get(id=target_id)
        target.status = data['status']
        target.save()

        return jsonify({
            'message': 'Target status updated successfully',
            'target': {
                'id': str(target.id),
                'name': target.name,
                'status': target.status
            }
        }), 200
    except Target.DoesNotExist:
        return jsonify({'error': 'Target not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to update status', 'detail': str(e)}), 500

# --- DELETE ---
def delete_target(target_id):
    """Remove criminal from surveillance database"""
    try:
        target = Target.objects.get(id=target_id)
        target_name = target.name
        target.delete()
        return jsonify({'message': f'Target {target_name} removed from surveillance system'}), 200
    except Target.DoesNotExist:
        return jsonify({'error': 'Target not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to delete target', 'detail': str(e)}), 500

# --- SURVEILLANCE SPECIFIC ---
def get_wanted_targets():
    """Get all wanted criminals for active surveillance monitoring"""
    try:
        targets = Target.objects(status='wanted')
        output = [{
            'id': str(target.id),
            'name': target.name,
            'identity_number': target.identity_number,
            'image_id': target.image_id,
            'address': target.address
        } for target in targets]

        return jsonify({
            'wanted_targets': output,
            'count': len(output),
            'message': 'Active surveillance targets'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve wanted targets', 'detail': str(e)}), 500

def get_convicted_targets():
    """Get all convicted criminals for records and verification"""
    try:
        targets = Target.objects(status='convicted')
        output = [{
            'id': str(target.id),
            'name': target.name,
            'identity_number': target.identity_number,
            'image_id': target.image_id,
            'address': target.address
        } for target in targets]

        return jsonify({
            'convicted_targets': output,
            'count': len(output),
            'message': 'Convicted criminals database'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve convicted targets', 'detail': str(e)}), 500

def get_under_trial_targets():
    """Get all under trial criminals for legal tracking"""
    try:
        targets = Target.objects(status='under_trial')
        output = [{
            'id': str(target.id),
            'name': target.name,
            'identity_number': target.identity_number,
            'image_id': target.image_id,
            'address': target.address
        } for target in targets]

        return jsonify({
            'under_trial_targets': output,
            'count': len(output),
            'message': 'Under trial criminals for legal tracking'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve under trial targets', 'detail': str(e)}), 500


def get_surveillance_statistics():
    """Get surveillance system statistics"""
    try:
        total_targets = Target.objects.count()
        status_counts = {
            'wanted': Target.objects(status='wanted').count(),
            'convicted': Target.objects(status='convicted').count(),
            'released': Target.objects(status='released').count()
        }

        return jsonify({
            'total_targets_in_system': total_targets,
            'status_distribution': status_counts,
            'active_surveillance_targets': status_counts['wanted'],
            'resolved_cases': status_counts['convicted'] + status_counts['released'],
            'pending_cases': status_counts['under_trial']
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve statistics', 'detail': str(e)}), 500

# --- FACE DETECTION MATCH ---
def match_detected_face():
    """Match detected face from surveillance camera with criminal database"""
    try:
        # Get image data from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        # Get image data as bytes
        image_data = image_file.read()
        
        # Get all wanted criminals with their image IDs for comparison
        wanted_targets = Target.objects(status='wanted')
        detected_matches = []
        
        # TODO: Implement your face recognition logic here
        # This is where you'd use OpenCV, face_recognition, or other ML libraries
        # Example structure:
        
        # for target in wanted_targets:
        #     if target.image_id:  # Make sure target has an image
        #         # Load target's stored image using target.image_id
        #         # stored_image = load_image_from_storage(target.image_id)
        #         
        #         # Compare detected face with stored criminal face
        #         # similarity = compare_faces(image_data, stored_image)
        #         
        #         # if similarity > 0.8:  # 80% match threshold
        #         #     detected_matches.append({
        #         #         'target_id': str(target.id),
        #         #         'name': target.name,
        #         #         'identity_number': target.identity_number,
        #         #         'image_id': target.image_id,
        #         #         'confidence': similarity,
        #         #         'status': target.status
        #         #     })

        # For now, return structure without actual face matching
        alert_level = 'high' if detected_matches else 'none'
        
        return jsonify({
            'matches_found': len(detected_matches),
            'detected_criminals': detected_matches,
            'timestamp': datetime.utcnow().isoformat(),
            'alert_level': alert_level,
            'total_wanted_in_database': wanted_targets.count(),
            'message': 'Face recognition scan completed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Face matching failed', 'detail': str(e)}), 500