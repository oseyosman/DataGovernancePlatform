# API Documentation
## Data Governance & Compliance Platform

**Author:** Osman Yildiz  
**Version:** 1.0.0

---

## Base URL

http://localhost:5000
---

## Authentication

All protected endpoints require a JWT token in the Authorization header:

Authorization: Bearer <your_jwt_token>

---

## Endpoints

### Health Check

**GET** `/health`

Check if API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Data Governance Platform API is running",
  "version": "1.0.0"
}
```

---

### User Registration

**POST** `/api/auth/register`

Register a new user.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "viewer"
}
```

**Roles:** `admin`, `compliance_officer`, `data_steward`, `viewer`

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "viewer",
    "is_active": true
  }
}
```

---

### User Login

**POST** `/api/auth/login`

Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "viewer"
  }
}
```

---

### Get Current User

**GET** `/api/auth/me`

Get current authenticated user information.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "viewer",
  "is_active": true
}
```

---

### Dashboard Overview

**GET** `/api/dashboard/overview`

Get dashboard statistics.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Dashboard overview loaded successfully",
  "current_user": {...},
  "statistics": {
    "total_users": 5,
    "active_users": 4,
    "inactive_users": 1,
    "users_by_role": {
      "admin": 1,
      "compliance_officer": 1,
      "data_steward": 2,
      "viewer": 1
    }
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid username or password"
}
```

### 403 Forbidden
```json
{
  "error": "Account is inactive"
}
```

### 404 Not Found
```json
{
  "error": "User not found"
}
```

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"Admin123!","role":"admin"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
```

### Dashboard (with token)
```bash
curl http://localhost:5000/api/dashboard/overview \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

