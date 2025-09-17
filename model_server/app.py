from flask import Flask
from flask_cors import CORS
import logging

from routes.model_face_routes import face_bp
from routes.model_attendance_routes import attendance_bp
from db import init_db

def create_app():
  app = Flask(__name__)
  CORS(app)
  
  # Initialize database connection
  init_db()

  app.register_blueprint(face_bp, url_prefix="/api/valid_face")
  app.register_blueprint(attendance_bp, url_prefix="/api/attendance")

  return app

if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
  )
  
  from face_recognition.engine import init_face_analysis, initialize_face_recognition

  print("Initializing face analysis...")
  face_analysis_initialized = init_face_analysis()
  print("Face analysis ready:", face_analysis_initialized)
  
  print("Initializing face recognition...")
  face_recognition_initialized = initialize_face_recognition()
  print("Face recognition ready:", face_recognition_initialized)


  app = create_app()
  app.run(debug=True, host="0.0.0.0", port=3000)
