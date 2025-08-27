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

```
http://localhost:5000
```

## Usage with Flutter App

### If running locally:

1. Find your machine's IP (e.g., 192.168.x.x).
2. Replace `localhost` in your Flutter API calls with that IP, e.g.:

```
http://192.168.x.x:5000/api/...
```

### If deployed on a server:

Use the server's public IP or domain instead.