# Backend Service Module

## Introduction

The Backend Service Module is one of the core components of the Intelligent Digital Human Mentor System, responsible for handling user authentication, session management, data storage, and communication with other modules. This module is developed based on the Flask framework and provides a series of RESTful APIs to support interaction between the frontend interface and other service modules.

## Key Features

- User authentication and authorization management
- Session management and state persistence
- Data storage and retrieval
- Communication interfaces with LLM, RAG, TTS, and other modules
- File upload and management
- Email notification services

## System Requirements

- Python 3.10 or higher
- SQLite or other compatible databases
- Redis cache service (optional, for performance improvement)
- SMTP server (for sending verification emails)

## Deployment Guide

Since this system does not use Docker for deployment, you can clone and deploy the backend service from GitHub using the following steps.

### 2.3.1 Clone the Repository

```bash
$ git clone git@github.com:unsw-cse-comp99-3900/capstone-project-25t2-9900-h16c-bread1.git
$ cd capstone-project-25t2-9900-h16c-bread1
```

### 2.3.2 Install Dependencies

#### Step 1 - Create and Activate the Conda Environment

```bash
$ conda create -n bread1 python=3.10 -y
$ conda activate bread1
```

#### Step 2 - Install Core Dependencies via Pip

```bash
$ pip install flask==3.1.1 \
flask-cors==6.0.1 \
flask-jwt-extended==4.7.0 \
flask-mail==0.10.0 \
flask-sqlalchemy==3.1.1 \
redis==5.0.3 \
requests==2.32.4
```

### 2.3.3 Configure and Run the Application

Update the port number in `run.py` to your desired running port, and modify the relevant settings in `config.py`, such as the lifespan of each token.

```bash
$ python run.py
```

### 2.3.4 Dependency File

You can also install all dependencies using the requirements.txt file:

```
# --- Core Backend Framework ---
flask==3.1.1
flask-cors==6.0.1
flask-jwt-extended==4.7.0
flask-mail==0.10.0
flask-sqlalchemy==3.1.1
werkzeug==3.1.3
jinja2==3.1.6
itsdangerous==2.2.0
blinker==1.9.0
markupsafe==3.0.2

# --- Database & Cache ---
sqlalchemy==2.0.39
redis==5.0.3
greenlet==3.1.1

# --- Networking & Security ---
requests==2.32.4
urllib3==2.5.0
charset-normalizer==3.4.2
idna==3.10
certifi==2025.6.15
pyjwt==2.10.1
pysocks==1.7.1

# --- Packaging & Typing ---
setuptools==78.1.1
wheel==0.45.1
typing-extensions==4.14.0
zipp==3.23.0
importlib-metadata==8.7.0
```

### 2.3.5 Environment Variables & Secrets

Create a `.env` file and set the following environment variables:

```
# Flask & Security
FLASK_ENV=production
SECRET_KEY=change_me_strong_random_string
JWT_SECRET_KEY=change_me_another_strong_random_string

# CORS
CORS_ORIGINS=http://localhost:5173

# Database
DATABASE_URL=sqlite:////data/app.db   # persisted in Docker volume

# Mail (send verification code)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_smtp_user
MAIL_PASSWORD=your_smtp_password
MAIL_DEFAULT_SENDER=noreply@example.com

# Redis
REDIS_URL=redis://redis:6379/0
```

## API Documentation

The backend service provides the following main APIs:

### User Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### User Management

- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Chat Functionality

- `POST /api/chat/send` - Send message
- `GET /api/chat/history` - Get chat history

### File Upload

- `POST /api/upload/file` - Upload file

## Common Issues

1. **Database Initialization Issues**: Before running for the first time, ensure the database is initialized:
   ```bash
   $ python -c "from models.user import db; from app import create_app; app = create_app(); app.app_context().push(); db.create_all()"
   ```

2. **Email Service Configuration**: Ensure the SMTP server settings are correct, otherwise verification emails cannot be sent.

3. **Redis Connection Issues**: If you don't need to use Redis, you can modify the relevant configuration in config.py.


