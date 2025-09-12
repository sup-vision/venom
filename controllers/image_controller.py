from flask import request, jsonify, send_file
from datetime import datetime
import io
import base64
try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False

from services.gridfs_service import gridfs_service

def upload_image():
    """Upload single or multiple images to GridFS with id and student_id metadata"""
    try:
        # Get form data
        image_files = request.files.getlist('images')
        
        if not image_files or all(file.filename == '' for file in image_files):
            return jsonify({
                'error': 'No image files provided'
            }), 400
        
        # Get metadata
        id = request.form.get('id')
        image_type = request.form.get('image_type', 'general')  # general, profile, attendance, etc.
        
        if not id:
            return jsonify({
                'error': 'id is required'
            }), 400
        
        # Validate ObjectId
        try:
            id_obj = gridfs_service.validate_object_id(id)
        except ValueError as e:
            return jsonify({
                'error': str(e)
            }), 400
        
        uploaded_images = []
        errors = []
        
        # Process each image
        for i, image_file in enumerate(image_files):
            try:
                if image_file.filename == '':
                    continue
                
                # Read image data
                image_data = image_file.read()
                
                # Validate image format
                try:
                    if IMAGEIO_AVAILABLE:
                        # Use imageio for validation
                        image_buffer = io.BytesIO(image_data)
                        img = imageio.imread(image_buffer)
                        # Check if image has valid dimensions
                        if len(img.shape) < 2:
                            raise ValueError("Invalid image dimensions")
                    else:
                        # Basic validation - check file size and magic bytes
                        if len(image_data) < 100:  # Too small to be a valid image
                            raise ValueError("File too small to be a valid image")
                        
                        # Check for common image magic bytes
                        magic_bytes = image_data[:4]
                        valid_formats = [
                            b'\xff\xd8\xff',  # JPEG
                            b'\x89PNG',      # PNG
                            b'GIF8',         # GIF
                            b'RIFF'          # WebP (partial check)
                        ]
                        
                        if not any(image_data.startswith(mb) for mb in valid_formats):
                            # Additional check for BMP
                            if not image_data.startswith(b'BM'):
                                raise ValueError("Unrecognized image format")
                except Exception as e:
                    errors.append(f'Image {i+1}: Invalid image format - {str(e)}')
                    continue
                
                # Prepare metadata
                metadata = {
                    'associated_id': id_obj,
                    'image_type': image_type,
                    'original_filename': image_file.filename,
                    'content_type': image_file.content_type,
                    'upload_date': datetime.utcnow(),
                    'file_size': len(image_data),
                    'batch_upload': True
                }
                
                # Upload to GridFS
                file_id = gridfs_service.upload_file(
                    image_data,
                    image_file.filename,
                    metadata
                )
                
                uploaded_images.append({
                    'file_id': str(file_id),
                    'filename': image_file.filename,
                    'file_size': len(image_data),
                    'content_type': image_file.content_type
                })
                
            except Exception as e:
                errors.append(f'Image {i+1}: {str(e)}')
        
        if not uploaded_images:
            return jsonify({
                'error': 'No images were successfully uploaded',
                'errors': errors
            }), 400
        
        response_data = {
            'message': f'Successfully uploaded {len(uploaded_images)} image(s)',
            'associated_id': id,
            'image_type': image_type,
            'uploaded_images': uploaded_images,
            'total_uploaded': len(uploaded_images),
            'total_attempted': len([f for f in image_files if f.filename != ''])
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['error_count'] = len(errors)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to upload images',
            'detail': str(e)
        }), 500

def get_image(file_id):
    """Retrieve an image from GridFS by file_id"""
    try:
        # Validate ObjectId
        try:
            file_id_obj = gridfs_service.validate_object_id(file_id)
        except ValueError as e:
            return jsonify({
                'error': str(e)
            }), 400
        
        # Get file info
        file_info = gridfs_service.get_file_info(file_id_obj)
        if not file_info:
            return jsonify({
                'error': 'Image not found'
            }), 404
        
        # Get file data
        file_data = gridfs_service.get_file(file_id_obj)
        
        # Return image as response
        return send_file(
            io.BytesIO(file_data),
            mimetype=file_info.content_type,
            as_attachment=False,
            download_name=file_info.filename
        )
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve image',
            'detail': str(e)
        }), 500

def get_image_metadata(file_id):
    """Get image metadata without downloading the actual image"""
    try:
        # Validate ObjectId
        try:
            file_id_obj = gridfs_service.validate_object_id(file_id)
        except ValueError as e:
            return jsonify({
                'error': str(e)
            }), 400
        
        # Get file info
        file_info = gridfs_service.get_file_info(file_id_obj)
        if not file_info:
            return jsonify({
                'error': 'Image not found'
            }), 404
        
        # Return metadata
        return jsonify({
            'file_id': str(file_info._id),
            'filename': file_info.filename,
            'content_type': file_info.content_type,
            'file_size': file_info.length,
            'upload_date': file_info.upload_date.isoformat(),
            'metadata': {
                'associated_id': str(file_info.metadata.get('associated_id')),
                'image_type': file_info.metadata.get('image_type'),
                'original_filename': file_info.metadata.get('original_filename')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get image metadata',
            'detail': str(e)
        }), 500

def get_images_by_user(id):
    """Get all images uploaded by a specific user"""
    try:
        # Validate ObjectId
        try:
            id_obj = gridfs_service.validate_object_id(id)
        except ValueError as e:
            return jsonify({
                'error': str(e)
            }), 400
        
        # Find all files for this user
        files = gridfs_service.find_files({'metadata.associated_id': id_obj})
        
        images = []
        for file_info in files:
            images.append({
                'file_id': str(file_info._id),
                'filename': file_info.filename,
                'content_type': file_info.content_type,
                'file_size': file_info.length,
                'upload_date': file_info.upload_date.isoformat(),
                'metadata': {
                    'associated_id': str(file_info.metadata.get('associated_id')),
                    'image_type': file_info.metadata.get('image_type'),
                    'original_filename': file_info.metadata.get('original_filename')
                }
            })
        
        return jsonify({
            'images': images,
            'count': len(images),
            'associated_id': id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get images by user',
            'detail': str(e)
        }), 500

def delete_image(file_id):
    """Delete an image from GridFS"""
    try:
        # Validate ObjectId
        try:
            file_id_obj = gridfs_service.validate_object_id(file_id)
        except ValueError as e:
            return jsonify({
                'error': str(e)
            }), 400
        
        # Check if file exists
        file_info = gridfs_service.get_file_info(file_id_obj)
        if not file_info:
            return jsonify({
                'error': 'Image not found'
            }), 404
        
        # Delete the file
        gridfs_service.delete_file(file_id_obj)
        
        return jsonify({
            'message': 'Image deleted successfully',
            'file_id': file_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete image',
            'detail': str(e)
        }), 500

def get_image_base64(file_id):
    """Get image as base64 encoded string"""
    try:
        # Validate ObjectId
        try:
            file_id_obj = gridfs_service.validate_object_id(file_id)
        except ValueError as e:
            return jsonify({
                'error': str(e)
            }), 400
        
        # Get file info
        file_info = gridfs_service.get_file_info(file_id_obj)
        if not file_info:
            return jsonify({
                'error': 'Image not found'
            }), 404
        
        # Get file data and convert to base64
        file_data = gridfs_service.get_file(file_id_obj)
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        return jsonify({
            'file_id': str(file_info._id),
            'filename': file_info.filename,
            'content_type': file_info.content_type,
            'base64_data': base64_data,
            'metadata': {
                'associated_id': str(file_info.metadata.get('associated_id')),
                'image_type': file_info.metadata.get('image_type')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get image as base64',
            'detail': str(e)
        }), 500
