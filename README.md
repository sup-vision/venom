# SupVision-Venom 🎓

A comprehensive **AI-powered attendance management system** that uses facial recognition technology to automatically track student attendance in educational institutions.

## 🚀 Project Overview

SupVision-Venom is a dual-service architecture consisting of:

1. **Main Application (`supvision/`)** - Flask-based REST API for managing students, schedules, attendance, and user authentication
2. **Model Server (`model_server/`)** - Dedicated service for face recognition processing using advanced AI models

### Key Features

- 🎯 **Automated Face Recognition** - Uses InsightFace and FAISS for high-accuracy student identification
- 📊 **Attendance Management** - Track and manage student attendance with detailed records
- 👥 **Student Management** - Complete CRUD operations for student data
- 📅 **Schedule Management** - Class scheduling and timetable management
- 🔐 **User Authentication** - Secure user management with bcrypt encryption
- 📸 **Image Processing** - Upload and process class photos for attendance
- 🗄️ **MongoDB Integration** - Scalable data storage with GridFS for image files
- 🐳 **Docker Support** - Easy deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main App      │    │  Model Server   │    │    MongoDB      │
│   (Port 5000)   │◄──►│   (Port 8000)   │◄──►│   (Port 27017)  │
│                 │    │                 │    │                 │
│ • Student Mgmt  │    │ • Face Analysis │    │ • Student Data  │
│ • Attendance    │    │ • Recognition   │    │ • Images (GridFS)│
│ • Schedules     │    │ • FAISS Index   │    │ • Attendance    │
│ • Authentication│    │ • Image Process │    │ • Schedules     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **MongoDB** - Database
- **PyMongo/MongoEngine** - Database ODM
- **GridFS** - File storage for images

### AI/ML
- **InsightFace** - Face analysis and recognition
- **FAISS** - Vector similarity search
- **OpenCV** - Image processing
- **NumPy** - Numerical computations

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Gunicorn** - WSGI server

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- MongoDB (if running locally)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd supVision-venom
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the services**
   - Main API: http://localhost:5000
   - Model Server: http://localhost:8000
   - MongoDB: localhost:27017

### Local Development

1. **Install dependencies**
   ```bash
   # Main application
   cd supvision
   pip install -r requirements.txt
   
   # Model server
   cd ../model_server
   pip install -r requirements.txt
   ```

2. **Start MongoDB**
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongo mongo:6.0
   
   # Or install MongoDB locally
   ```

3. **Run the services**
   ```bash
   # Terminal 1 - Main application
   cd supvision
   python app.py
   
   # Terminal 2 - Model server
   cd model_server
   python app.py
   ```

## 📚 API Endpoints

### Main Application (Port 5000)

#### Students
- `GET /api/v1/students` - Get all students
- `POST /api/v1/students` - Create student
- `GET /api/v1/students/<id>` - Get student by ID
- `PUT /api/v1/students/<id>` - Update student
- `DELETE /api/v1/students/<id>` - Delete student

#### Attendance
- `GET /api/v1/attendance` - Get attendance records
- `POST /api/v1/attendance` - Create attendance record
- `GET /api/v1/attendance/<id>` - Get attendance by ID

#### Recognition
- `POST /api/v1/recognition/process` - Process face recognition
- `POST /api/v1/recognition/upload` - Upload student images
- `GET /api/v1/recognition/status` - Get recognition status

#### Images
- `POST /api/v1/images/upload` - Upload images
- `GET /api/v1/images/<id>` - Get image by ID

### Model Server (Port 8000)

#### Face Recognition
- `POST /api/valid_face/process` - Process face recognition
- `POST /api/valid_face/initialize` - Initialize face recognition system

#### Files
- `POST /api/files/upload` - Upload files to GridFS
- `GET /api/files/<id>` - Download file by ID

## 📊 Data Models

### Student
```json
{
  "name": "Ashutosh Saha",
  "roll_number": "18700124043",
  "email": "ashutosh.saha.cse.2024@tint.edu.in",
  "phone": "9883319587",
  "section": "A",
  "semester": "3",
  "batch": "2024",
  "course": "B.Tech",
  "branch": "CSE",
  "face_embedding": "<binary_data>"
}
```

### Schedule
```json
{
  "subject_code": "PCCCS301",
  "subject_name": "Data Structure and Algorithm",
  "associative_fac_id": "68c319d6ad4b6fded6908977",
  "branch": "CSE",
  "semester": "3",
  "section": "A",
  "day": "Wednesday",
  "time": "09:30 AM"
}
```

## 🔧 Configuration

### Environment Variables

```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017/venom

# Flask
FLASK_ENV=development
FLASK_APP=app.py
DEBUG=True
```

### Docker Configuration

The `docker-compose.yml` file configures:
- MongoDB service with persistent volume
- Main application service
- Model server service
- Network connectivity between services

## 🎯 Usage Workflow

1. **Setup Students**: Add student records with face embeddings
2. **Create Schedule**: Define class schedules and subjects
3. **Upload Class Photos**: Upload images of the class
4. **Process Attendance**: Use face recognition to identify students
5. **View Reports**: Access attendance records and analytics

## 🔍 Face Recognition Process

1. **Image Upload**: Class photos are uploaded to the system
2. **Face Detection**: InsightFace detects faces in the images
3. **Feature Extraction**: Face embeddings are extracted and normalized
4. **Matching**: FAISS performs similarity search against student database
5. **Attendance Marking**: Students are identified and marked present/absent

## 🛡️ Security Features

- Password hashing with bcrypt
- Secure file upload validation
- CORS configuration for cross-origin requests
- Input validation and sanitization

## 📝 Development Notes

- The system uses FAISS for efficient vector similarity search
- Face embeddings are stored as binary data in MongoDB
- Images are stored using GridFS for scalability
- The model server can be scaled independently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed description
3. Include logs and error messages

---

**SupVision-Venom** - Making attendance management intelligent and automated! 🎓✨
