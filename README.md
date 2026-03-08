# Flask Authentication Microservice

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Railway](https://img.shields.io/badge/Deployed-Railway-purple)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black)

A production-ready Authentication Microservice built with Flask, featuring JWT authentication, OAuth2 Google login, Redis token blacklisting, Role-Based Access Control (RBAC), and rate limiting.

## 🔗 Live Demo
**Base URL:** `https://flask-auth-service-production.up.railway.app`

---

## 🏗️ Architecture

```
Client
  │
  ▼
Flask App (Gunicorn)
  │
  ├── PostgreSQL (User data, Password resets, OAuth accounts)
  └── Redis (Token blacklisting, Rate limiting)
```

---

## ✨ Features

- **JWT Authentication** — Access tokens (15 min) + Refresh tokens (7 days)
- **Token Blacklisting** — Redis-based logout that invalidates tokens immediately
- **Token Refresh** — Rotate refresh tokens on every use
- **OAuth2 Google Login** — Sign in with Google
- **RBAC** — Role-based access control (admin, user, moderator)
- **Rate Limiting** — 10 req/min for auth, 5 req/min for password reset
- **Password Reset** — Secure token-based password reset flow
- **Gunicorn** — Production WSGI server
- **Docker** — Fully containerized with Docker Compose
- **CI/CD** — GitHub Actions for automated testing and DockerHub push

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Framework | Flask 3.1, Flask-RESTful |
| Database | PostgreSQL 15, SQLAlchemy, Flask-Migrate |
| Cache | Redis 7 |
| Auth | PyJWT, bcrypt, Authlib (OAuth2) |
| Rate Limiting | Flask-Limiter |
| Server | Gunicorn |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions, DockerHub |
| Deployment | Railway |

---

## 📁 Project Structure

```
flask-auth-service/
├── app/
│   ├── __init__.py           # App factory
│   ├── config.py             # Configuration classes
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py           # User, TokenBlacklist, PasswordReset, OAuthAccount
│   ├── routes/
│   │   ├── auth.py           # Register, login, logout, profile
│   │   ├── token.py          # Refresh, verify token
│   │   └── oauth.py          # Google OAuth2
│   ├── services/
│   │   ├── auth_service.py   # Business logic
│   │   └── token_service.py  # JWT generation, blacklisting
│   ├── middleware/
│   │   └── rate_limit.py     # Rate limit config
│   └── utils/
│       └── decorators.py     # JWT, RBAC decorators
├── migrations/               # Database migrations
├── Dockerfile
├── docker-compose.yml
├── railway.json
├── start.sh
├── run.py
└── requirements.txt
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login with email/password | No |
| POST | `/auth/logout` | Logout and blacklist token | Yes |
| GET | `/auth/me` | Get current user profile | Yes |
| PUT | `/auth/me` | Update profile | Yes |
| DELETE | `/auth/me` | Delete account | Yes |

### Token
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/refresh-token` | Get new access + refresh token | No |
| POST | `/auth/verify-token` | Verify token validity | No |

### Password Reset
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/forgot-password` | Generate reset token | No |
| POST | `/auth/reset-password` | Reset password with token | No |

### OAuth2
| Method | Endpoint | Description |
|---|---|---|
| GET | `/auth/google` | Initiate Google login |
| GET | `/auth/google/callback` | Google OAuth2 callback |

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |

---

## 🚀 Running Locally

### Prerequisites
- Docker and Docker Compose
- Python 3.11+

### With Docker (Recommended)
```bash
# Clone repo
git clone https://github.com/Nihal2999/flask-auth-service.git
cd flask-auth-service

# Create .env file
cp .env.example .env  # Update values

# Start all services
docker-compose up --build

# App runs at http://localhost:5000
```

### Without Docker
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env

# Run migrations
flask db upgrade

# Start app
python run.py
```

---

## ⚙️ Environment Variables

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:password@localhost:5432/flask_auth_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

## 🧪 Testing the API

### Register
```bash
curl -X POST https://flask-auth-service-production.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "nihal", "email": "nihal@test.com", "password": "Test@1234"}'
```

### Login
```bash
curl -X POST https://flask-auth-service-production.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "nihal@test.com", "password": "Test@1234"}'
```

### Get Profile
```bash
curl -X GET https://flask-auth-service-production.up.railway.app/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token
```bash
curl -X POST https://flask-auth-service-production.up.railway.app/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

---

## 🔄 CI/CD Pipeline

```
git push → GitHub Actions
              │
              ├── Run Tests (PostgreSQL + Redis services)
              │
              └── Build & Push to DockerHub (nihal12999/flask-auth-service:latest)
                        │
                        └── Railway auto-deploys on push to main
```

---

## 🗄️ Database Models

```
User
├── id, username, email, password_hash
├── role (user/admin/moderator)
├── is_active, is_verified
└── created_at, updated_at

TokenBlacklist
└── token, blacklisted_at

PasswordReset
└── user_id, token, expires_at, used

OAuthAccount
└── user_id, provider, provider_id
```

---

## 🔐 Security Features

- Passwords hashed with **bcrypt**
- JWT tokens with expiry and unique `jti` (JWT ID)
- Blacklisted tokens stored in **Redis** with TTL
- Rate limiting on sensitive endpoints
- RBAC with decorator-based role enforcement
- OAuth2 with Google for social login

---

## 📦 Docker Setup

```yaml
services:
  app:     Flask + Gunicorn (port 5000)
  postgres: PostgreSQL 15 (port 5432)
  redis:    Redis 7 (port 6379)
```

---

## 🔮 Future Improvements

- Add email verification on register
- Add 2FA (Two-Factor Authentication)
- Add GitHub OAuth2
- Add unit and integration tests
- Add Nginx reverse proxy
- Deploy on AWS ECS