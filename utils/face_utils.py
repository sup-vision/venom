# utils/face_utils.py
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import logging
import pickle
from bson.binary import Binary

# Initialize Face Analysis
face_app = None

def init_face_app():
    """Initialize the face analysis application"""
    global face_app
    if face_app is None:
        try:
            face_app = FaceAnalysis(name="buffalo_l")
            face_app.prepare(ctx_id=0, det_size=(640, 640))
            logging.info("Face Analysis initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Face Analysis: {str(e)}")
            face_app = None
    return face_app

def extract_face_embedding(image_file):
    """Extract face embedding from an image file"""
    global face_app
    
    if face_app is None:
        init_face_app()
        if face_app is None:
            return None, "Face analysis system not available"
    
    try:
        # Read image from file
        image_data = image_file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None, "Failed to decode image"
        
        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = face_app.get(img_rgb)
        
        if not faces:
            return None, "No faces detected in the image"
        
        # Use the first/main face
        face = faces[0]
        embedding = face.embedding
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        
        # Serialize the embedding for storage
        serialized_embedding = pickle.dumps(embedding)
        
        return Binary(serialized_embedding), None
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"