# SupVision-Venom

## Overview

SupVision-Venom is a backend service built using Flask, connected to MongoDB, and containerized with Docker. It provides APIs for user management and can be consumed by frontend apps such as Flutter.

## Features

- RESTful API with Flask
- MongoDB database (via Docker)
- Containerized using Docker and Docker Compose
- Accessible on any device in the same network (or remotely if hosted on a server)

## Project Structure

```
supVision-venom/
├── controllers/        # API controllers
├── models/            # Database models
├── routes/            # API route definitions
├── app.py             # Main application entry point
├── db.py              # MongoDB connection setup
├── config.py          # App configuration
├── Dockerfile         # Container build setup for Flask
├── docker-compose.yml # Orchestration for Flask + MongoDB services
└── requirements.txt   # Python dependencies
```

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

1. Clone the repository.
2. Make sure Docker is installed and running.
3. Build and start the containers using:

```bash
docker-compose up --build
```

The API will be available at:

**http://localhost:5000**

## Usage with Flutter App

### If running locally:

1. Find your machine's IP (e.g., 192.168.x.x).
2. Replace `localhost` in your Flutter API calls with that IP, e.g.:

```
http://192.168.x.x:5000/api/...
```

### If deployed on a server:

Use the server's public IP or domain instead.

## API Endpoints

### User Management
- **Base URL (Local)**: `http://localhost:5000/api/v1/users`
- **Base URL (External)**: `http://YOUR_LOCAL_IP:5000/api/v1/users`
- **GET** `/api/v1/users` - Get all users
- **POST** `/api/v1/users` - Create a new user
- **GET** `/api/v1/users/<id>` - Get user by ID
- **PUT** `/api/v1/users/<id>` - Update user
- **DELETE** `/api/v1/users/<id>` - Delete user

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
1. **Docker Container Issues**: Ensure Docker and Docker Compose are running
2. **Port Already in Use**: Check if port 5000 is available or change it in docker-compose.yml
3. **MongoDB Connection Error**: Verify MongoDB container is running via `docker-compose ps`

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