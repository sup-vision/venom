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
cd supVision-venom
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
# Start MongoDB service
# On macOS (if installed via Homebrew)
brew services start mongodb-community

# On Ubuntu/Debian
sudo systemctl start mongod

# On Windows
net start MongoDB
```

The application is configured to connect to `mongodb://localhost:27017/venom` by default.

### 5. Configuration
The application uses the default configuration from `config.py`. You can modify:
- `DEBUG` mode
- `SECRET_KEY` for production
- `MONGO_URI` if using a different MongoDB connection

## Running the Application

### Step-by-Step Running Instructions

#### Step 1: Activate Virtual Environment
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### Step 2: Verify MongoDB is Running
```bash
# Check if MongoDB is running
mongo --eval "db.runCommand('ping')" || echo "MongoDB is not running"
```

#### Step 3: Start the Flask Application
```bash
python app.py
```

#### Step 4: Verify the Application is Running
You should see output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Development Mode
The server will start on `http://localhost:5000` with debug mode enabled.

### Accessing from External Devices

To access the application from other devices on your network:

1. **Find your local IP address:**
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows
   ipconfig | findstr "IPv4"
   ```

2. **Access the application using your local IP:**
   - **Base URL for external devices**: `http://YOUR_LOCAL_IP:5000`
   - **Example**: If your local IP is `192.168.1.100`, use `http://192.168.1.100:5000`

3. **API Endpoints for external devices:**
   - **User Management**: `http://YOUR_LOCAL_IP:5000/api/v1/users`

**Note**: Make sure your firewall allows connections on port 5000, and that other devices are on the same network.

## API Endpoints

### User Management
- **Base URL (Local)**: `http://localhost:5000/api/v1/users`
- **Base URL (External)**: `http://YOUR_LOCAL_IP:5000/api/v1/users`
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