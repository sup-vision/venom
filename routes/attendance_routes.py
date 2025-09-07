#routes/attendance_routes.py
from flask import Blueprint, request, jsonify, current_app
import cv2
import numpy as np
import logging
from insightface.app import FaceAnalysis
import pickle
from werkzeug.utils import secure_filename
import tempfile
import os
from datetime import datetime
from functools import wraps

# Create blueprint
bp = Blueprint('attendance', __name__, url_prefix='/api/v1/attendance')

# Global variables for face recognition
face_app = None
index = None
student_embeddings = {}
student_details = {}

def init_attendance_system():
    """Initialize the attendance system"""
    global face_app
    
    try:
        # Initialize Face Analysis
        face_app = FaceAnalysis(name="buffalo_l")
        face_app.prepare(ctx_id=0, det_size=(640, 640))
        logging.info("Face Analysis initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize attendance system: {str(e)}")
        face_app = None

def requires_attendance_init(f):
    """Decorator to check if attendance system is initialized"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if face_app is None:
            return jsonify({'error': 'Attendance system not initialized'}), 503
        return f(*args, **kwargs)
    return decorated_function

def initialize_face_recognition():
    """Initialize the face recognition system with data from MongoDB"""
    global index, student_embeddings, student_details
    
    # Clear previous data
    student_embeddings = {}
    student_details = {}
    
    try:
        # Get students collection from app context
        with current_app.app_context():
            students_collection = current_app.db.students
            
            # Fetch all student records from MongoDB
            students = students_collection.find({})
            
            embeddings_list = []
            names_list = []
            
            for student in students:
                student_id = str(student['_id'])
                name = student.get('name', 'Unknown')
                roll_number = student.get('roll_number', '')
                
                # Store student details
                student_details[student_id] = {
                    'name': name,
                    'roll_number': roll_number,
                    'student_id': student_id
                }
                
                # Get embedding from MongoDB
                if 'face_embedding' in student:
                    # Deserialize the embedding
                    embedding = pickle.loads(student['face_embedding'])
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    student_embeddings[student_id] = embedding
                    embeddings_list.append(embedding)
                    names_list.append(student_id)
            
            if not embeddings_list:
                logging.warning("No student embeddings found in database!")
                return False
            
            # Create FAISS index
            import faiss
            d = len(embeddings_list[0])
            embeddings_array = np.array(embeddings_list, dtype="float32")
            
            # Use FlatIP for cosine similarity
            index = faiss.IndexFlatIP(d)
            index.add(embeddings_array)
            
            logging.info(f"Initialized face recognition with {len(embeddings_list)} students")
            return True
            
    except Exception as e:
        logging.error(f"Error initializing face recognition: {str(e)}")
        return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def process_image(image_path):
    """Process a single image and return recognized students"""
    # Configuration
    BASE_THRESHOLD = 0.40
    SMALL_FACE_THRESHOLD = 0.35
    LARGE_FACE_THRESHOLD = 0.48
    MARGIN_DELTA = 0.04
    MIN_FACE_SIZE = 20
    
    if face_app is None:
        logging.error("Face Analysis not initialized")
        return []
    
    img = cv2.imread(image_path)
    if img is None:
        logging.warning(f"Failed to load image: {image_path}")
        return []
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_app.get(img_rgb)
    
    recognized_students = set()
    
    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        w, h = x2 - x1, y2 - y1
        face_size = min(w, h)
        
        if face_size < 40:
            sim_thresh = SMALL_FACE_THRESHOLD
        elif face_size > 100:
            sim_thresh = LARGE_FACE_THRESHOLD
        else:
            sim_thresh = BASE_THRESHOLD
        
        if face_size < MIN_FACE_SIZE:
            continue  # Skip faces that are too small
        
        embedding = face.embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        # Search for similar faces in the database
        try:
            import faiss
            similarities, indices = index.search(np.array([embedding], dtype="float32"), k=2)
            
            if len(similarities) > 0 and len(indices) > 0:
                s1, s2 = float(similarities[0, 0]), float(similarities[0, 1])
                candidate_id = list(student_embeddings.keys())[int(indices[0, 0])]
                
                # Check if the face matches our threshold criteria
                if s1 >= sim_thresh and (s1 - s2) >= MARGIN_DELTA:
                    recognized_students.add(candidate_id)
        except Exception as e:
            logging.error(f"Error during face search: {str(e)}")
    
    return list(recognized_students)

@bp.route('/take', methods=['POST'])
@requires_attendance_init
def take_attendance():
    """Take attendance from uploaded crowd images"""
    try:
        # Check if files are present in the request
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        
        # Validate number of files
        if len(files) > 6:
            return jsonify({'error': 'Maximum 6 images allowed'}), 400
        
        # Check if any valid files were uploaded
        valid_files = [f for f in files if f and allowed_file(f.filename)]
        if not valid_files:
            return jsonify({'error': 'No valid image files provided'}), 400
        
        # Initialize face recognition if not already done
        if index is None:
            if not initialize_face_recognition():
                return jsonify({'error': 'Failed to initialize face recognition'}), 500
        
        # Create temporary directory for uploads
        upload_folder = tempfile.mkdtemp()
        
        # Process each image
        all_recognized_students = set()
        temp_files = []
        
        try:
            for file in valid_files:
                # Save uploaded file temporarily
                filename = secure_filename(file.filename)
                temp_file_path = os.path.join(upload_folder, filename)
                file.save(temp_file_path)
                temp_files.append(temp_file_path)
                
                # Process the image
                recognized = process_image(temp_file_path)
                all_recognized_students.update(recognized)
        
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            if os.path.exists(upload_folder):
                os.rmdir(upload_folder)
        
        # Prepare response with student details
        present_students = []
        for student_id in all_recognized_students:
            if student_id in student_details:
                present_students.append(student_details[student_id])
        
        # Save attendance record to database
        with current_app.app_context():
            attendance_record = {
                'timestamp': datetime.utcnow(),
                'present_students': present_students,
                'total_present': len(present_students),
                'images_processed': len(valid_files)
            }
            
            current_app.db.attendance_records.insert_one(attendance_record)
        
        return jsonify({
            'success': True,
            'attendance_record': attendance_record
        })
        
    except Exception as e:
        logging.error(f"Error taking attendance: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for attendance system"""
    status = {
        'face_recognition_initialized': face_app is not None,
        'students_loaded': len(student_embeddings),
        'faiss_index_ready': index is not None
    }
    
    return jsonify(status)

@bp.route('/reinitialize', methods=['POST'])
@requires_attendance_init
def reinitialize():
    """Reinitialize the face recognition system"""
    try:
        success = initialize_face_recognition()
        if success:
            return jsonify({
                'success': True,
                'message': f'Face recognition reinitialized with {len(student_embeddings)} students'
            })
        else:
            return jsonify({'error': 'Failed to reinitialize'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/records', methods=['GET'])
def get_attendance_records():
    """Get all attendance records"""
    try:
        with current_app.app_context():
            records_cursor = current_app.db.attendance_records.find({}).sort('timestamp', -1)
            records = []
            for record in records_cursor:
                # Convert ObjectId to string for JSON serialization
                record['_id'] = str(record['_id'])
                records.append(record)
            
            return jsonify({
                'success': True,
                'records': records
            })
    except Exception as e:
        logging.error(f"Error fetching attendance records: {str(e)}")
        return jsonify({'error': 'Failed to fetch records'}), 500

# Initialize the attendance system when the module is imported
init_attendance_system()