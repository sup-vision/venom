import cv2
import numpy as np
import faiss
import pickle
import logging
from insightface.app import FaceAnalysis
from db import students_collection, mongodb_available

# Global variables for face recognition
face_app = None
index = None
student_embeddings = None
student_details = None
id_map = None
initialized = False
face_app_available = False

def init_face_analysis():
    """Initialize only the FaceAnalysis part"""
    global face_app
    try:
        face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        face_app.prepare(ctx_id=0, det_size=(640, 640))
        logging.info("✅ FaceAnalysis initialized")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to initialize FaceAnalysis: {str(e)}")
        return False

def initialize_face_recognition():
    """Initialize the complete face recognition system"""
    global face_app, index, student_embeddings, student_details, id_map, initialized
    
    if face_app is None:
        if not init_face_analysis():
            return False

    if not mongodb_available:
        logging.error("❌ MongoDB not available")
        return False

    student_embeddings, student_details, id_map = {}, {}, {}
    embeddings_list, ids_list = [], []

    try:
        students = students_collection.find({})
        for student in students:
            student_id = student["_id"]
            name = student.get("name", "Unknown")
            roll_number = student.get("roll_number", "")

            student_details[str(student_id)] = {
                "name": name,
                "roll_number": roll_number,
                "student_id": str(student_id)
            }

            embedding_bin = student.get("face_embedding")
            if embedding_bin:
                try:
                    embedding = pickle.loads(embedding_bin)
                    if embedding is not None and embedding.size > 0:
                        embedding = embedding.astype("float32")
                        embedding /= np.linalg.norm(embedding)

                        student_embeddings[str(student_id)] = embedding
                        embeddings_list.append(embedding)
                        ids_list.append(student_id)
                except Exception as e:
                    logging.warning(f"⚠️ Skipped student {student_id}: bad embedding ({str(e)})")

        if not embeddings_list:
            logging.error("❌ No valid embeddings found in DB")
            return False

        d = embeddings_list[0].shape[0]

        index = faiss.IndexIDMap(faiss.IndexFlatIP(d))
        embeddings_array = np.array(embeddings_list, dtype="float32")

        int_ids = [hash(str(s)) % (1 << 63) for s in ids_list]
        id_array = np.array(int_ids, dtype="int64")

        id_map = {int_ids[i]: ids_list[i] for i in range(len(ids_list))}

        index.add_with_ids(embeddings_array, id_array)

        logging.info(f"✅ Loaded {len(embeddings_list)} students into FAISS")
        initialized = True
        return True

    except Exception as e:
        logging.error(f"❌ FAISS initialization failed: {str(e)}")
        return False

def is_initialized():
    """Check if the face recognition system is initialized"""
    return initialized and face_app is not None and index is not None

def ensure_initialized():
    """Ensure the face recognition system is initialized, try to initialize if not"""
    if is_initialized():
        return True
    
    logging.warning("Face recognition not initialized. Attempting to initialize...")
    return initialize_face_recognition()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path):
    """Process a single image and return recognized students with details"""
    if not ensure_initialized():
        logging.error("Face recognition system could not be initialized")
        return []
    
    # Configuration
    BASE_THRESHOLD = 0.40
    SMALL_FACE_THRESHOLD = 0.35
    LARGE_FACE_THRESHOLD = 0.48
    MIN_FACE_SIZE = 20
    
    img = cv2.imread(image_path)
    if img is None:
        logging.warning(f"Failed to load image: {image_path}")
        return []
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    try:
        faces = face_app.get(img_rgb)
        
        if faces is None:
            logging.warning(f"No faces detected in image: {image_path}")
            return []
            
        recognized_students = []
        
        for face in faces:
            if not hasattr(face, 'bbox') or not hasattr(face, 'normed_embedding'):
                continue
                
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
            
            embedding = face.normed_embedding
            if embedding is None:
                continue
                
            embedding = embedding.astype("float32")
            embedding = embedding / np.linalg.norm(embedding)
            
            try:
                similarities, indices = index.search(np.array([embedding], dtype="float32"), k=3)
                
                if len(similarities) > 0 and len(indices) > 0:
                    best_match = None
                    best_confidence = 0
                    
                    for i in range(len(similarities[0])):
                        similarity_score = float(similarities[0, i])
                        faiss_id = int(indices[0, i])
                        
                        if similarity_score >= sim_thresh and similarity_score > best_confidence:
                            if faiss_id in id_map:
                                best_match = str(id_map[faiss_id])
                                best_confidence = similarity_score
                    
                    if best_match:
                        details = student_details.get(best_match, {})
                        
                        recognized_students.append({
                            "student_id": best_match,
                            "name": details.get("name", "Unknown"),
                            "roll_number": details.get("roll_number", ""),
                            "confidence": best_confidence,
                            "bbox": [int(x1), int(y1), int(x2), int(y2)]
                        })
                        logging.info(f"Recognized student {best_match} with confidence {best_confidence:.3f}")
                        
            except Exception as e:
                logging.error(f"Error during face search: {str(e)}")
                continue
        
        return recognized_students
        
    except Exception as e:
        logging.error(f"Error detecting faces in image {image_path}: {str(e)}")
        return []

def get_face_app():
    return face_app

def get_index():
    return index

def get_student_details():
    return student_details

def get_id_map():
    return id_map