# Server side for SupVision

## Project Overview
This is a Flask-based REST API server for SupVision, featuring user management with MongoDB integration.

## Prerequisites
- Python 3.8 or higher
- MongoDB installed and running locally
- pip (Python package installer)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd venom
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. MongoDB Setup
Make sure MongoDB is running on your local machine:
```bash
The application is configured to connect to `mongodb://localhost:27017/venom` by default.
```

### 5. Configuration
The application uses the default configuration from `config.py`. You can modify:
- `DEBUG` mode
- `SECRET_KEY` for production
- `MONGO_URI` if using a different MongoDB connection

## Running the Application

### Development Mode
```bash
python app.py
```

The server will start on `http://localhost:5000` with debug mode enabled.

## API Endpoints

### User Management
- **Base URL**: `/api/v1/users`
- **GET** `/api/v1/users` - Get all users
- **POST** `/api/v1/users` - Create a new user
- **GET** `/api/v1/users/<id>` - Get user by ID
- **PUT** `/api/v1/users/<id>` - Update user
- **DELETE** `/api/v1/users/<id>` - Delete user

## Project Structure
```
supVision-venom/
├── app.py              # Main application entry point
├── config.py           # Configuration settings
├── controllers/        # Business logic controllers
│   └── user_controller.py
├── models/            # Data models
│   └── user_model.py
├── routes/            # API route definitions
│   └── user_routes.py
└── requirements.txt   # Python dependencies
```

## Development

### Adding New Features
1. Create models in the `models/` directory
2. Add controllers in the `controllers/` directory
3. Define routes in the `routes/` directory
4. Register new blueprints in `app.py`

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes

## Troubleshooting

### Common Issues
1. **MongoDB Connection Error**: Ensure MongoDB is running and accessible
2. **Port Already in Use**: Change the port in `app.py` or kill the process using the port
3. **Import Errors**: Make sure you're in the correct directory and virtual environment is activated

### Debug Mode
The application runs in debug mode by default, which provides:
- Detailed error messages
- Auto-reload on code changes
- Interactive debugger

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request