---
title: Zovryn Finance Dashboard - API Documentation
version: 1.0.0
base_url: http://localhost:3000
content_type: application/json
authentication: Bearer JWT Token
rate_limit: 100 requests / 15 minutes / IP
tags:
  - api
  - rest
  - documentation
  - postman
---

# Zovryn Finance Dashboard - API Documentation

> Complete API reference for the Zovryn Finance Dashboard Backend. Includes all endpoints, request/response examples, and Postman testing guide.

---

## Base Configuration

```yaml
base_url: http://localhost:3000
content_type: application/json
authentication: Bearer Token (JWT)
rate_limit:
  window: 15 minutes
  max_requests: 100
  scope: per IP address
```

---

## Quick Start

```bash
# 1. Clone and install
npm install

# 2. Setup environment
cp .env.example .env

# 3. Start development server
npm run dev

# 4. Seed database with sample data
npm run seed

# 5. Server running at http://localhost:3000
```

---

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```yaml
header:
  key: Authorization
  value: "Bearer <your_jwt_token>"
  example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### How to Get a Token

1. Register a new user via `POST /api/auth/register`
2. Login via `POST /api/auth/login` - returns a `token` in the response
3. Use the token in the `Authorization` header for all protected requests

### Token Details

```yaml
algorithm: HS256
expires_in: 24h (default)
payload:
  id: number
  email: string
  name: string
  role: viewer | analyst | admin
  status: active | inactive
```

---

## Role Permissions

```yaml
viewer:
  - GET /api/auth/me
  - GET /api/records
  - GET /api/records/:id

analyst:
  - All viewer permissions
  - GET /api/dashboard/summary
  - GET /api/dashboard/categories
  - GET /api/dashboard/trends/monthly
  - GET /api/dashboard/trends/weekly

admin:
  - All analyst permissions
  - POST /api/records
  - PATCH /api/records/:id
  - DELETE /api/records/:id
  - GET /api/users
  - GET /api/users/:id
  - PATCH /api/users/:id
  - DELETE /api/users/:id
```

---

## Endpoints

---

### Health Check

#### `GET /health`

```yaml
auth_required: false
description: Check if the server is running
```

**cURL**

```bash
curl http://localhost:3000/health
```

**Response** `200 OK`

```json
{
  "status": "ok"
}
```

---

### Auth Routes

---

#### `POST /api/auth/register`

```yaml
auth_required: false
description: Register a new user account
default_role: viewer
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "Jane Doe"
}
```

**Validation Rules**

```yaml
email:
  type: string
  required: true
  format: valid email
password:
  type: string
  required: true
  min_length: 8
name:
  type: string
  required: true
  min_length: 1
  max_length: 100
```

**cURL**

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "Jane Doe"
  }'
```

**Response** `201 Created`

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Jane Doe",
  "role": "viewer",
  "status": "active",
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T10:00:00.000Z"
}
```

**Errors**

```yaml
400 Bad Request:
  - Invalid email format
  - Password less than 8 characters
  - Missing or empty name
  example: { "error": "Validation failed", "details": [{ "field": "password", "message": "String must contain at least 8 character(s)" }] }

409 Conflict:
  - Email already registered
  example: { "error": "Email already registered" }
```

---

#### `POST /api/auth/login`

```yaml
auth_required: false
description: Authenticate and receive a JWT token
```

**Request Body**

```json
{
  "email": "admin@example.com",
  "password": "password123"
}
```

**Validation Rules**

```yaml
email:
  type: string
  required: true
  format: valid email
password:
  type: string
  required: true
  min_length: 1
```

**cURL**

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

**Response** `200 OK`

```json
{
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin",
    "status": "active",
    "created_at": "2026-04-02T10:00:00.000Z",
    "updated_at": "2026-04-02T10:00:00.000Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsIm5hbWUiOiJBZG1pbiBVc2VyIiwicm9sZSI6ImFkbWluIiwic3RhdHVzIjoiYWN0aXZlIn0..."
}
```

**Errors**

```yaml
401 Unauthorized:
  - Invalid email or password
  example: { "error": "Invalid email or password" }

403 Forbidden:
  - Account is inactive
  example: { "error": "Account is inactive" }
```

---

#### `GET /api/auth/me`

```yaml
auth_required: true
roles: [viewer, analyst, admin]
description: Get the currently authenticated user's profile
```

**Headers**

```yaml
Authorization: "Bearer <token>"
```

**cURL**

```bash
curl http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

**Response** `200 OK`

```json
{
  "id": 1,
  "email": "admin@example.com",
  "name": "Admin User",
  "role": "admin",
  "status": "active",
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T10:00:00.000Z"
}
```

**Errors**

```yaml
401 Unauthorized:
  - Missing or invalid token
  - Token expired
  - Account inactive
  example: { "error": "Invalid token" }
```

---

### User Management Routes

> All routes require `admin` role

---

#### `GET /api/users`

```yaml
auth_required: true
roles: [admin]
description: List all users with pagination
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
```

**Query Parameters**

```yaml
page:
  type: integer
  required: false
  default: 1
  min: 1
  example: "?page=2"
limit:
  type: integer
  required: false
  default: 20
  min: 1
  max: 100
  example: "?limit=10"
```

**cURL**

```bash
curl "http://localhost:3000/api/users?page=1&limit=20" \
  -H "Authorization: Bearer <admin_token>"
```

**Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "email": "admin@example.com",
      "name": "Admin User",
      "role": "admin",
      "status": "active",
      "created_at": "2026-04-02T10:00:00.000Z",
      "updated_at": "2026-04-02T10:00:00.000Z"
    },
    {
      "id": 2,
      "email": "analyst@example.com",
      "name": "Analyst User",
      "role": "analyst",
      "status": "active",
      "created_at": "2026-04-02T10:00:00.000Z",
      "updated_at": "2026-04-02T10:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 3,
    "totalPages": 1
  }
}
```

**Errors**

```yaml
401 Unauthorized:
  - Not authenticated or not admin role
  example: { "error": "Not authorized" }
```

---

#### `GET /api/users/:id`

```yaml
auth_required: true
roles: [admin]
description: Get a specific user by ID
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
```

**Path Parameters**

```yaml
id:
  type: integer
  required: true
  description: User ID
  example: /api/users/1
```

**cURL**

```bash
curl http://localhost:3000/api/users/1 \
  -H "Authorization: Bearer <admin_token>"
```

**Response** `200 OK`

```json
{
  "id": 1,
  "email": "admin@example.com",
  "name": "Admin User",
  "role": "admin",
  "status": "active",
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T10:00:00.000Z"
}
```

**Errors**

```yaml
400 Bad Request:
  - Invalid user ID format
  example: { "error": "Invalid user ID" }

404 Not Found:
  - User does not exist
  example: { "error": "User not found" }
```

---

#### `PATCH /api/users/:id`

```yaml
auth_required: true
roles: [admin]
description: Update a user's name, role, or status
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
Content-Type: application/json
```

**Path Parameters**

```yaml
id:
  type: integer
  required: true
  description: User ID
  example: /api/users/3
```

**Request Body** (at least one field required)

```json
{
  "name": "Updated Name",
  "role": "analyst",
  "status": "inactive"
}
```

**cURL**

```bash
curl -X PATCH http://localhost:3000/api/users/3 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "role": "analyst",
    "status": "inactive"
  }'
```

**Validation Rules**

```yaml
name:
  type: string
  required: false
  min_length: 1
  max_length: 100
role:
  type: string
  required: false
  enum: [viewer, analyst, admin]
status:
  type: string
  required: false
  enum: [active, inactive]
```

**Response** `200 OK`

```json
{
  "id": 3,
  "email": "viewer@example.com",
  "name": "Updated Name",
  "role": "analyst",
  "status": "inactive",
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T11:30:00.000Z"
}
```

**Errors**

```yaml
400 Bad Request:
  - Invalid user ID
  - No fields provided
  - Invalid role or status value
  example: { "error": "Validation failed", "details": [{ "field": "role", "message": "Invalid enum value" }] }

404 Not Found:
  - User does not exist
  example: { "error": "User not found" }
```

---

#### `DELETE /api/users/:id`

```yaml
auth_required: true
roles: [admin]
description: Permanently delete a user (hard delete)
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
```

**Path Parameters**

```yaml
id:
  type: integer
  required: true
  description: User ID
  example: /api/users/3
```

**cURL**

```bash
curl -X DELETE http://localhost:3000/api/users/3 \
  -H "Authorization: Bearer <admin_token>"
```

**Response** `204 No Content`

```yaml
body: empty
```

**Errors**

```yaml
400 Bad Request:
  - Invalid user ID
  example: { "error": "Invalid user ID" }

404 Not Found:
  - User does not exist
  example: { "error": "User not found" }
```

---

### Financial Records Routes

---

#### `GET /api/records`

```yaml
auth_required: true
roles: [viewer, analyst, admin]
description: List financial records with filtering, search, and pagination
```

**Headers**

```yaml
Authorization: "Bearer <token>"
```

**Query Parameters**

```yaml
page:
  type: integer
  required: false
  default: 1
  min: 1
limit:
  type: integer
  required: false
  default: 20
  min: 1
  max: 100
type:
  type: string
  required: false
  enum: [income, expense]
  description: Filter by record type
  example: "?type=income"
category:
  type: string
  required: false
  description: Filter by exact category name
  example: "?category=Salary"
startDate:
  type: string
  required: false
  format: YYYY-MM-DD
  description: Filter records from this date
  example: "?startDate=2026-01-01"
endDate:
  type: string
  required: false
  format: YYYY-MM-DD
  description: Filter records until this date
  example: "?endDate=2026-03-31"
search:
  type: string
  required: false
  description: Search in description and category (LIKE query)
  example: "?search=salary"
```

**cURL**

```bash
curl "http://localhost:3000/api/records?type=income&startDate=2026-01-01&endDate=2026-03-31&page=1&limit=10" \
  -H "Authorization: Bearer <token>"
```

**Example Request**

```
GET /api/records?type=income&startDate=2026-01-01&endDate=2026-03-31&page=1&limit=10
```

**Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "amount": 5000,
      "type": "income",
      "category": "Salary",
      "date": "2026-01-15",
      "description": "Monthly salary",
      "is_deleted": 0,
      "created_at": "2026-04-02T10:00:00.000Z",
      "updated_at": "2026-04-02T10:00:00.000Z"
    },
    {
      "id": 4,
      "user_id": 1,
      "amount": 5000,
      "type": "income",
      "category": "Salary",
      "date": "2026-02-15",
      "description": "Monthly salary",
      "is_deleted": 0,
      "created_at": "2026-04-02T10:00:00.000Z",
      "updated_at": "2026-04-02T10:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 6,
    "totalPages": 1
  }
}
```

---

#### `GET /api/records/:id`

```yaml
auth_required: true
roles: [viewer, analyst, admin]
description: Get a single financial record by ID
note: Returns 404 if record is soft-deleted
```

**Headers**

```yaml
Authorization: "Bearer <token>"
```

**Path Parameters**

```yaml
id:
  type: integer
  required: true
  description: Record ID
  example: /api/records/1
```

**cURL**

```bash
curl http://localhost:3000/api/records/1 \
  -H "Authorization: Bearer <token>"
```

**Response** `200 OK`

```json
{
  "id": 1,
  "user_id": 1,
  "amount": 5000,
  "type": "income",
  "category": "Salary",
  "date": "2026-01-15",
  "description": "Monthly salary",
  "is_deleted": 0,
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T10:00:00.000Z"
}
```

**Errors**

```yaml
400 Bad Request:
  - Invalid record ID format
  example: { "error": "Invalid record ID" }

404 Not Found:
  - Record does not exist or is soft-deleted
  example: { "error": "Record not found" }
```

---

#### `POST /api/records`

```yaml
auth_required: true
roles: [admin]
description: Create a new financial record
note: The user_id is automatically set from the authenticated user
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
Content-Type: application/json
```

**Request Body**

```json
{
  "amount": 5000,
  "type": "income",
  "category": "Salary",
  "date": "2026-01-15",
  "description": "Monthly salary"
}
```

**Validation Rules**

```yaml
amount:
  type: number
  required: true
  constraint: must be positive (> 0)
type:
  type: string
  required: true
  enum: [income, expense]
category:
  type: string
  required: true
  min_length: 1
  max_length: 50
date:
  type: string
  required: true
  format: YYYY-MM-DD
  regex: "^\\d{4}-\\d{2}-\\d{2}$"
description:
  type: string
  required: false
  max_length: 500
```

**cURL**

```bash
curl -X POST http://localhost:3000/api/records \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "type": "income",
    "category": "Salary",
    "date": "2026-01-15",
    "description": "Monthly salary"
  }'
```

**Response** `201 Created`

```json
{
  "id": 17,
  "user_id": 1,
  "amount": 5000,
  "type": "income",
  "category": "Salary",
  "date": "2026-01-15",
  "description": "Monthly salary",
  "is_deleted": 0,
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T10:00:00.000Z"
}
```

**Errors**

```yaml
400 Bad Request:
  - Missing required fields
  - Negative or zero amount
  - Invalid type enum
  - Invalid date format
  - Category too long
  example: { "error": "Validation failed", "details": [{ "field": "amount", "message": "Number must be greater than 0" }] }

401 Unauthorized:
  - Not authenticated or not admin
  example: { "error": "Not authorized" }
```

---

#### `PATCH /api/records/:id`

```yaml
auth_required: true
roles: [admin]
description: Update an existing financial record
note: At least one field must be provided
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
Content-Type: application/json
```

**Path Parameters**

```yaml
id:
  type: integer
  required: true
  description: Record ID
  example: /api/records/1
```

**Request Body** (at least one field required)

```json
{
  "amount": 6000,
  "category": "Bonus",
  "description": "Updated salary with bonus"
}
```

**Validation Rules**

```yaml
amount:
  type: number
  required: false
  constraint: must be positive (> 0)
type:
  type: string
  required: false
  enum: [income, expense]
category:
  type: string
  required: false
  min_length: 1
  max_length: 50
date:
  type: string
  required: false
  format: YYYY-MM-DD
description:
  type: string
  required: false
  max_length: 500
```

**cURL**

```bash
curl -X PATCH http://localhost:3000/api/records/1 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 6000,
    "category": "Bonus",
    "description": "Updated salary with bonus"
  }'
```

**Response** `200 OK`

```json
{
  "id": 1,
  "user_id": 1,
  "amount": 6000,
  "type": "income",
  "category": "Bonus",
  "date": "2026-01-15",
  "description": "Updated salary with bonus",
  "is_deleted": 0,
  "created_at": "2026-04-02T10:00:00.000Z",
  "updated_at": "2026-04-02T11:30:00.000Z"
}
```

**Errors**

```yaml
400 Bad Request:
  - Invalid record ID
  - No fields provided
  - Invalid field values
  example: { "error": "Validation failed", "details": [...] }

404 Not Found:
  - Record does not exist
  example: { "error": "Record not found" }
```

---

#### `DELETE /api/records/:id`

```yaml
auth_required: true
roles: [admin]
description: Soft delete a financial record
note: Sets is_deleted = 1, does NOT permanently remove the record
```

**Headers**

```yaml
Authorization: "Bearer <admin_token>"
```

**Path Parameters**

```yaml
id:
  type: integer
  required: true
  description: Record ID
  example: /api/records/5
```

**cURL**

```bash
curl -X DELETE http://localhost:3000/api/records/5 \
  -H "Authorization: Bearer <admin_token>"
```

**Response** `204 No Content`

```yaml
body: empty
```

**Errors**

```yaml
400 Bad Request:
  - Invalid record ID
  example: { "error": "Invalid record ID" }

404 Not Found:
  - Record does not exist
  example: { "error": "Record not found" }
```

---

### Dashboard Analytics Routes

> All routes require `analyst` or `admin` role

---

#### `GET /api/dashboard/summary`

```yaml
auth_required: true
roles: [analyst, admin]
description: Get financial summary with totals, category breakdown, recent activity, and monthly trends
```

**Headers**

```yaml
Authorization: "Bearer <analyst_or_admin_token>"
```

**Query Parameters**

```yaml
startDate:
  type: string
  required: false
  format: YYYY-MM-DD
  description: Filter summary from this date
endDate:
  type: string
  required: false
  format: YYYY-MM-DD
  description: Filter summary until this date
```

**cURL**

```bash
curl "http://localhost:3000/api/dashboard/summary?startDate=2026-01-01&endDate=2026-03-31" \
  -H "Authorization: Bearer <analyst_or_admin_token>"
```

**Example Request**

```
GET /api/dashboard/summary?startDate=2026-01-01&endDate=2026-03-31
```

**Response** `200 OK`

```json
{
  "totalIncome": 16100,
  "totalExpenses": 5085,
  "netBalance": 11015,
  "recordCount": 16,
  "categoryTotals": [
    {
      "category": "Salary",
      "total": 15000
    },
    {
      "category": "Rent",
      "total": 3600
    },
    {
      "category": "Freelance",
      "total": 800
    },
    {
      "category": "Groceries",
      "total": 750
    },
    {
      "category": "Utilities",
      "total": 460
    },
    {
      "category": "Healthcare",
      "total": 300
    },
    {
      "category": "Investment",
      "total": 200
    },
    {
      "category": "Refund",
      "total": 100
    },
    {
      "category": "Transport",
      "total": 75
    },
    {
      "category": "Entertainment",
      "total": 50
    }
  ],
  "recentActivity": [
    {
      "id": 16,
      "amount": 100,
      "type": "income",
      "category": "Refund",
      "date": "2026-03-10",
      "description": "Product refund"
    }
  ],
  "monthlyTrends": [
    {
      "month": "2026-01",
      "income": 5000,
      "expense": 1750,
      "net": 3250
    },
    {
      "month": "2026-02",
      "income": 5800,
      "expense": 2085,
      "net": 3715
    },
    {
      "month": "2026-03",
      "income": 5300,
      "expense": 1250,
      "net": 4050
    }
  ]
}
```

**Notes**

```yaml
recent_activity: Returns last 10 records by date
monthly_trends: Returns up to last 12 months
category_totals: Sorted by total amount descending
```

---

#### `GET /api/dashboard/categories`

```yaml
auth_required: true
roles: [analyst, admin]
description: Get category breakdown of financial records
```

**Headers**

```yaml
Authorization: "Bearer <analyst_or_admin_token>"
```

**Query Parameters**

```yaml
type:
  type: string
  required: false
  enum: [income, expense]
  description: Filter categories by record type
  example: "?type=expense"
```

**cURL**

```bash
curl "http://localhost:3000/api/dashboard/categories?type=expense" \
  -H "Authorization: Bearer <analyst_or_admin_token>"
```

**Response** `200 OK`

```json
[
  {
    "category": "Salary",
    "total": 15000
  },
  {
    "category": "Rent",
    "total": 3600
  },
  {
    "category": "Freelance",
    "total": 800
  }
]
```

**Example with Type Filter**

```
GET /api/dashboard/categories?type=expense
```

```json
[
  {
    "category": "Rent",
    "total": 3600
  },
  {
    "category": "Groceries",
    "total": 750
  },
  {
    "category": "Utilities",
    "total": 460
  }
]
```

---

#### `GET /api/dashboard/trends/monthly`

```yaml
auth_required: true
roles: [analyst, admin]
description: Get monthly income/expense trends for the last 12 months
```

**Headers**

```yaml
Authorization: "Bearer <analyst_or_admin_token>"
```

**cURL**

```bash
curl http://localhost:3000/api/dashboard/trends/monthly \
  -H "Authorization: Bearer <analyst_or_admin_token>"
```

**Response** `200 OK`

```json
[
  {
    "month": "2026-01",
    "income": 5000,
    "expense": 1750,
    "net": 3250
  },
  {
    "month": "2026-02",
    "income": 5800,
    "expense": 2085,
    "net": 3715
  },
  {
    "month": "2026-03",
    "income": 5300,
    "expense": 1250,
    "net": 4050
  }
]
```

---

#### `GET /api/dashboard/trends/weekly`

```yaml
auth_required: true
roles: [analyst, admin]
description: Get weekly income/expense trends for the last 12 weeks
```

**Headers**

```yaml
Authorization: "Bearer <analyst_or_admin_token>"
```

**cURL**

```bash
curl http://localhost:3000/api/dashboard/trends/weekly \
  -H "Authorization: Bearer <analyst_or_admin_token>"
```

**Response** `200 OK`

```json
[
  {
    "week": "2026-W10",
    "income": 1500,
    "expense": 400,
    "net": 1100
  },
  {
    "week": "2026-W11",
    "income": 2000,
    "expense": 600,
    "net": 1400
  },
  {
    "week": "2026-W12",
    "income": 1800,
    "expense": 250,
    "net": 1550
  }
]
```

---

## Error Response Formats

### Standard Error

```json
{
  "error": "Error message here"
}
```

### Validation Error

```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    },
    {
      "field": "password",
      "message": "String must contain at least 8 character(s)"
    }
  ]
}
```

### Common HTTP Status Codes

```yaml
200 OK: Successful request
201 Created: Resource successfully created
204 No Content: Successful deletion
400 Bad Request: Invalid input or validation error
401 Unauthorized: Missing/invalid token or insufficient role
403 Forbidden: Account is inactive
404 Not Found: Resource does not exist
409 Conflict: Duplicate resource (e.g., email already registered)
429 Too Many Requests: Rate limit exceeded
500 Internal Server Error: Unexpected server error
```

---

## Postman Testing Guide

### Step 1: Import or Create Collection

Create a new Postman collection named **"Zovryn Finance Dashboard"**.

### Step 2: Set Up Environment Variables

Create a Postman Environment named **"Zovryn Local"** with these variables:

```yaml
variables:
  base_url:
    initial_value: "http://localhost:3000"
    current_value: "http://localhost:3000"
  admin_token:
    initial_value: ""
    current_value: ""
  analyst_token:
    initial_value: ""
    current_value: ""
  viewer_token:
    initial_value: ""
    current_value: ""
```

### Step 3: Seed the Database

Before testing, run the seed command to populate sample data:

```bash
npm run seed
```

This creates three test users:

```yaml
admin:
  email: admin@example.com
  password: password123
  role: admin
analyst:
  email: analyst@example.com
  password: password123
  role: analyst
viewer:
  email: viewer@example.com
  password: password123
  role: viewer
```

### Step 4: Configure Requests

---

#### Request 1: Health Check

```yaml
method: GET
url: "{{base_url}}/health"
headers: none
body: none
expected_status: 200
```

---

#### Request 2: Login as Admin

```yaml
method: POST
url: "{{base_url}}/api/auth/login"
headers:
  Content-Type: application/json
body_raw_json: |
  {
    "email": "admin@example.com",
    "password": "password123"
  }
expected_status: 200
```

**Post-response Script** (add in Postman "Tests" tab):

```javascript
var jsonData = pm.response.json();
pm.environment.set("admin_token", jsonData.token);
```

---

#### Request 3: Login as Analyst

```yaml
method: POST
url: "{{base_url}}/api/auth/login"
headers:
  Content-Type: application/json
body_raw_json: |
  {
    "email": "analyst@example.com",
    "password": "password123"
  }
expected_status: 200
```

**Post-response Script**:

```javascript
var jsonData = pm.response.json();
pm.environment.set("analyst_token", jsonData.token);
```

---

#### Request 4: Login as Viewer

```yaml
method: POST
url: "{{base_url}}/api/auth/login"
headers:
  Content-Type: application/json
body_raw_json: |
  {
    "email": "viewer@example.com",
    "password": "password123"
  }
expected_status: 200
```

**Post-response Script**:

```javascript
var jsonData = pm.response.json();
pm.environment.set("viewer_token", jsonData.token);
```

---

#### Request 5: Register New User

```yaml
method: POST
url: "{{base_url}}/api/auth/register"
headers:
  Content-Type: application/json
body_raw_json: |
  {
    "email": "newuser@example.com",
    "password": "securepass123",
    "name": "New User"
  }
expected_status: 201
```

---

#### Request 6: Get My Profile

```yaml
method: GET
url: "{{base_url}}/api/auth/me"
headers:
  Authorization: "Bearer {{admin_token}}"
body: none
expected_status: 200
```

---

#### Request 7: List All Users (Admin Only)

```yaml
method: GET
url: "{{base_url}}/api/users?page=1&limit=20"
headers:
  Authorization: "Bearer {{admin_token}}"
body: none
expected_status: 200
```

---

#### Request 8: Get User by ID (Admin Only)

```yaml
method: GET
url: "{{base_url}}/api/users/2"
headers:
  Authorization: "Bearer {{admin_token}}"
body: none
expected_status: 200
```

---

#### Request 9: Update User (Admin Only)

```yaml
method: PATCH
url: "{{base_url}}/api/users/3"
headers:
  Authorization: "Bearer {{admin_token}}"
  Content-Type: application/json
body_raw_json: |
  {
    "role": "analyst",
    "name": "Promoted Viewer"
  }
expected_status: 200
```

---

#### Request 10: Delete User (Admin Only)

```yaml
method: DELETE
url: "{{base_url}}/api/users/4"
headers:
  Authorization: "Bearer {{admin_token}}"
body: none
expected_status: 204
```

---

#### Request 11: List Records (All Roles)

```yaml
method: GET
url: "{{base_url}}/api/records?page=1&limit=10"
headers:
  Authorization: "Bearer {{viewer_token}}"
body: none
expected_status: 200
```

---

#### Request 12: List Records with Filters

```yaml
method: GET
url: "{{base_url}}/api/records?type=income&startDate=2026-01-01&endDate=2026-03-31&search=salary"
headers:
  Authorization: "Bearer {{viewer_token}}"
body: none
expected_status: 200
```

---

#### Request 13: Get Record by ID

```yaml
method: GET
url: "{{base_url}}/api/records/1"
headers:
  Authorization: "Bearer {{viewer_token}}"
body: none
expected_status: 200
```

---

#### Request 14: Create Record (Admin Only)

```yaml
method: POST
url: "{{base_url}}/api/records"
headers:
  Authorization: "Bearer {{admin_token}}"
  Content-Type: application/json
body_raw_json: |
  {
    "amount": 2500,
    "type": "expense",
    "category": "Equipment",
    "date": "2026-04-01",
    "description": "New laptop for development"
  }
expected_status: 201
```

---

#### Request 15: Update Record (Admin Only)

```yaml
method: PATCH
url: "{{base_url}}/api/records/1"
headers:
  Authorization: "Bearer {{admin_token}}"
  Content-Type: application/json
body_raw_json: |
  {
    "amount": 5500,
    "description": "Monthly salary - updated with raise"
  }
expected_status: 200
```

---

#### Request 16: Delete Record (Admin Only)

```yaml
method: DELETE
url: "{{base_url}}/api/records/5"
headers:
  Authorization: "Bearer {{admin_token}}"
body: none
expected_status: 204
```

---

#### Request 17: Dashboard Summary (Analyst/Admin)

```yaml
method: GET
url: "{{base_url}}/api/dashboard/summary"
headers:
  Authorization: "Bearer {{analyst_token}}"
body: none
expected_status: 200
```

---

#### Request 18: Dashboard Summary with Date Range

```yaml
method: GET
url: "{{base_url}}/api/dashboard/summary?startDate=2026-01-01&endDate=2026-01-31"
headers:
  Authorization: "Bearer {{analyst_token}}"
body: none
expected_status: 200
```

---

#### Request 19: Category Breakdown (Analyst/Admin)

```yaml
method: GET
url: "{{base_url}}/api/dashboard/categories"
headers:
  Authorization: "Bearer {{analyst_token}}"
body: none
expected_status: 200
```

---

#### Request 20: Category Breakdown by Type

```yaml
method: GET
url: "{{base_url}}/api/dashboard/categories?type=expense"
headers:
  Authorization: "Bearer {{analyst_token}}"
body: none
expected_status: 200
```

---

#### Request 21: Monthly Trends (Analyst/Admin)

```yaml
method: GET
url: "{{base_url}}/api/dashboard/trends/monthly"
headers:
  Authorization: "Bearer {{analyst_token}}"
body: none
expected_status: 200
```

---

#### Request 22: Weekly Trends (Analyst/Admin)

```yaml
method: GET
url: "{{base_url}}/api/dashboard/trends/weekly"
headers:
  Authorization: "Bearer {{analyst_token}}"
body: none
expected_status: 200
```

---

### Step 5: Test Role-Based Access Control

Test that roles are enforced by trying restricted endpoints with wrong tokens:

```yaml
test_cases:
  viewer_cannot_create_record:
    method: POST
    url: "{{base_url}}/api/records"
    headers:
      Authorization: "Bearer {{viewer_token}}"
      Content-Type: application/json
    body: |
      { "amount": 100, "type": "income", "category": "Test", "date": "2026-04-01" }
    expected_status: 401

  viewer_cannot_access_dashboard:
    method: GET
    url: "{{base_url}}/api/dashboard/summary"
    headers:
      Authorization: "Bearer {{viewer_token}}"
    expected_status: 401

  analyst_cannot_create_record:
    method: POST
    url: "{{base_url}}/api/records"
    headers:
      Authorization: "Bearer {{analyst_token}}"
      Content-Type: application/json
    body: |
      { "amount": 100, "type": "income", "category": "Test", "date": "2026-04-01" }
    expected_status: 401

  analyst_cannot_manage_users:
    method: GET
    url: "{{base_url}}/api/users"
    headers:
      Authorization: "Bearer {{analyst_token}}"
    expected_status: 401

  unauthenticated_cannot_access_records:
    method: GET
    url: "{{base_url}}/api/records"
    headers: none
    expected_status: 401
```

---

### Step 6: Test Validation Errors

```yaml
test_cases:
  register_invalid_email:
    method: POST
    url: "{{base_url}}/api/auth/register"
    body: |
      { "email": "not-an-email", "password": "password123", "name": "Test" }
    expected_status: 400

  register_short_password:
    method: POST
    url: "{{base_url}}/api/auth/register"
    body: |
      { "email": "test@test.com", "password": "short", "name": "Test" }
    expected_status: 400

  create_record_negative_amount:
    method: POST
    url: "{{base_url}}/api/records"
    headers:
      Authorization: "Bearer {{admin_token}}"
    body: |
      { "amount": -500, "type": "income", "category": "Test", "date": "2026-04-01" }
    expected_status: 400

  create_record_invalid_date:
    method: POST
    url: "{{base_url}}/api/records"
    headers:
      Authorization: "Bearer {{admin_token}}"
    body: |
      { "amount": 500, "type": "income", "category": "Test", "date": "04-01-2026" }
    expected_status: 400

  create_record_invalid_type:
    method: POST
    url: "{{base_url}}/api/records"
    headers:
      Authorization: "Bearer {{admin_token}}"
    body: |
      { "amount": 500, "type": "transfer", "category": "Test", "date": "2026-04-01" }
    expected_status: 400
```

---

### Postman Tips

```yaml
tips:
  - Use "Collection Runner" to run all requests in sequence
  - Login requests should run first to populate token variables
  - Use "Pre-request Script" to add dynamic data
  - Use "Tests" tab to auto-save tokens and validate responses
  - Set Content-Type to "application/json" in collection-level headers
  - Use {{base_url}} variable so you can switch between local and deployed
```

### Postman Pre-request Script (Collection Level)

Add this at the collection level to auto-set Content-Type:

```javascript
pm.request.headers.add({
    key: 'Content-Type',
    value: 'application/json'
});
```

### Postman Test Script Template

Use this template in the "Tests" tab for any request:

```javascript
// Check status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Check response is JSON
pm.test("Response is JSON", function () {
    pm.response.to.be.json;
});

// Check response time
pm.test("Response time is less than 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Save token (for login requests)
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    if (jsonData.token) {
        pm.environment.set("admin_token", jsonData.token);
    }
}
```
