import cv2
import pickle
import numpy as np
from insightface.app import FaceAnalysis
from db import students_collection
from bson.binary import Binary

face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=-1, det_size=(640, 640))

def is_blurry(image_path, threshold=80):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    fm = cv2.Laplacian(image, cv2.CV_64F).var()
    return fm < threshold, fm

def validate_face(image_file, student_id):
    """
    Validate face quality and store ArcFace embedding in MongoDB
    - Rejects blurry images
    - Rejects if no/multiple faces
    - Saves normalized embedding (no photo_path)
    """
    result = {"valid": False, "reason": ""}

    student = students_collection.find_one({"_id": student_id})
    if not student:
        result["reason"] = "Student not found in DB"
        return result

    try:
        if isinstance(image_file, str):
            img = cv2.imread(image_file)
            if img is None:
                result["reason"] = f"Cannot read image from path: {image_file}"
                return result
        else:
            image_data = image_file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                result["reason"] = "Invalid image format"
                return result

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        if fm < 80:
            result["reason"] = f"Image too blurry (score={fm:.2f})"
            return result

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = face_app.get(img_rgb)

        if len(faces) == 0:
            result["reason"] = "No face detected"
            return result

        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))

        embedding = face.embedding.astype("float32")
        embedding = embedding / np.linalg.norm(embedding)

        students_collection.update_one(
            {"_id": student_id},
            {"$set": {"face_embedding": Binary(pickle.dumps(embedding))}}
        )

        result["valid"] = True
        result["reason"] = "Face saved successfully"
        result["embedding"] = embedding.tolist()
        return result

    except Exception as e:
        result["reason"] = f"Error processing image: {str(e)}"
        return result


'''
The following code is for testing purposes only.
'''

# def register_all_students(student_images):
#     """
#     Register faces for all students in the provided dictionary
#     student_images: dict mapping student_id to image_path
#     """
#     results = {}
    
#     for student_id, image_path in student_images.items():
#         if isinstance(student_id, str):
#             student_id = ObjectId(student_id)
            
#         print(f"Processing student {student_id} with image {image_path}")
        
#         if not os.path.exists(image_path):
#             print(f"Warning: Image not found at {image_path}")
#             results[student_id] = {"valid": False, "reason": "Image file not found"}
#             continue
            
#         result = validate_face(image_path, student_id)
#         results[student_id] = result
        
#         if result["valid"]:
#             print(f"✅ Successfully registered face for student {student_id}")
#         else:
#             print(f"❌ Failed to register face for student {student_id}: {result['reason']}")
    
#     return results

# student_images = {
#     "68c4609da0e61c0a23b5d6b5": "/Users/skakibahammed/code_playground/Recognition/datasets/targets/18700124187.jpg",
#     "68c4609da0e61c0a23b5d6b6": "/Users/skakibahammed/code_playground/Recognition/datasets/targets/18700124047.jpg",
# }

# registration_results = register_all_students(student_images)

# print("\n=== Registration Summary ===")
# success_count = sum(1 for result in registration_results.values() if result["valid"])
# print(f"Successfully registered: {success_count}/{len(registration_results)}")

# for student_id, result in registration_results.items():
#     status = "✅" if result["valid"] else "❌"
#     print(f"{status} Student {student_id}: {result['reason']}")