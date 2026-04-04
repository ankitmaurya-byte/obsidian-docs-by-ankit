---
title: Zovryn Finance Dashboard Backend
version: 1.0.0
type: RESTful API
status: active
created: 2026-04-02
tags:
  - nodejs
  - typescript
  - express
  - sqlite
  - jwt
  - rbac
  - finance
---

# Zovryn Finance Dashboard Backend

> A finance dashboard backend with role-based access control (RBAC) for managing financial records (income/expense tracking) and providing analytics.

---

## Overview

```yaml
project_name: zovryn-finance-dashboard
description: Finance dashboard backend with role-based access control
runtime: Node.js
language: TypeScript
framework: Express 5
database: SQLite (better-sqlite3)
authentication: JWT (JSON Web Tokens)
validation: Zod
testing: Vitest + Supertest
rate_limiting: express-rate-limit (100 req / 15 min / IP)
cors: Enabled globally
```

---

## Tech Stack

```yaml
production:
  - bcryptjs: ^3.0.3          # Password hashing
  - better-sqlite3: ^12.8.0   # SQLite driver
  - cors: ^2.8.6              # CORS middleware
  - dotenv: ^17.3.1           # Environment variables
  - express: ^5.2.1           # Web framework
  - express-rate-limit: ^8.3.2 # Rate limiting
  - jsonwebtoken: ^9.0.3      # JWT handling
  - zod: ^4.3.6               # Schema validation

development:
  - typescript: ^6.0.2        # Type system
  - tsx: ^4.21.0              # TypeScript executor
  - vitest: ^4.1.2            # Test framework
  - supertest: ^7.2.2         # HTTP testing
  - ts-node: ^10.9.2          # TypeScript runtime
```

---

## Project Structure

```yaml
root: /
  src/:
    config/:
      - database.ts            # SQLite connection, schema, migrations
      - env.ts                 # Environment configuration
    middleware/:
      - auth.ts                # JWT authentication + role authorization
      - errorHandler.ts        # Global error handler
    models/:
      - user.ts                # User type definitions
      - record.ts              # Financial record type definitions
    routes/:
      - auth.ts                # Register, login, profile
      - users.ts               # User management (admin only)
      - records.ts             # CRUD for financial records
      - dashboard.ts           # Summary & analytics endpoints
    services/:
      - userService.ts         # User business logic
      - recordService.ts       # Record business logic
      - dashboardService.ts    # Analytics & aggregation
    utils/:
      - errors.ts              # Custom error classes
      - pagination.ts          # Pagination helpers
    - app.ts                   # Express app setup
    - index.ts                 # Entry point
    - seed.ts                  # Database seeder
  tests/:
    - setup.ts                 # Test configuration
    - auth.test.ts             # Authentication tests
    - records.test.ts          # Records CRUD + access control
    - dashboard.test.ts        # Dashboard analytics tests
  data/:                       # SQLite database storage
  - .env.example               # Environment variables template
  - package.json
  - tsconfig.json
  - vitest.config.ts
```

---

## Database Schema

### Users Table

```yaml
table: users
columns:
  id:
    type: INTEGER
    constraints: PRIMARY KEY AUTOINCREMENT
  email:
    type: TEXT
    constraints: UNIQUE NOT NULL
  password_hash:
    type: TEXT
    constraints: NOT NULL
  name:
    type: TEXT
    constraints: NOT NULL
  role:
    type: TEXT
    constraints: NOT NULL DEFAULT 'viewer'
    check: IN ('viewer', 'analyst', 'admin')
  status:
    type: TEXT
    constraints: NOT NULL DEFAULT 'active'
    check: IN ('active', 'inactive')
  created_at:
    type: TEXT
    constraints: NOT NULL DEFAULT datetime('now')
  updated_at:
    type: TEXT
    constraints: NOT NULL DEFAULT datetime('now')
```

### Financial Records Table

```yaml
table: financial_records
columns:
  id:
    type: INTEGER
    constraints: PRIMARY KEY AUTOINCREMENT
  user_id:
    type: INTEGER
    constraints: NOT NULL
    foreign_key: users(id)
  amount:
    type: REAL
    constraints: NOT NULL
  type:
    type: TEXT
    constraints: NOT NULL
    check: IN ('income', 'expense')
  category:
    type: TEXT
    constraints: NOT NULL
  date:
    type: TEXT
    constraints: NOT NULL
  description:
    type: TEXT
    constraints: nullable
  is_deleted:
    type: INTEGER
    constraints: NOT NULL DEFAULT 0
  created_at:
    type: TEXT
    constraints: NOT NULL DEFAULT datetime('now')
  updated_at:
    type: TEXT
    constraints: NOT NULL DEFAULT datetime('now')

indexes:
  - idx_records_user_id: financial_records(user_id)
  - idx_records_type: financial_records(type)
  - idx_records_category: financial_records(category)
  - idx_records_date: financial_records(date)
  - idx_records_is_deleted: financial_records(is_deleted)
```

---

## Role-Based Access Control (RBAC)

```yaml
roles:
  viewer:
    description: Default role for new users
    permissions:
      - View financial records
      - View own profile
  analyst:
    description: Can access dashboard analytics
    permissions:
      - View financial records
      - View own profile
      - View dashboard summary
      - View category breakdown
      - View monthly/weekly trends
  admin:
    description: Full system access
    permissions:
      - All viewer permissions
      - All analyst permissions
      - Create financial records
      - Update financial records
      - Delete financial records (soft delete)
      - Manage users (CRUD)
      - Change user roles and status
```

---

## Environment Configuration

```yaml
variables:
  PORT:
    default: 3000
    type: integer
    description: Server listening port
  JWT_SECRET:
    default: dev-secret-change-in-production
    type: string
    description: JWT signing secret key
  JWT_EXPIRES_IN:
    default: 24h
    type: string
    description: Token expiration time
  BCRYPT_ROUNDS:
    default: 10
    type: integer
    description: Password hashing rounds
  DB_PATH:
    default: ./data/finance.db
    type: string
    description: SQLite database file path
```

---

## Middleware Stack

```yaml
global:
  - cors: Cross-Origin Resource Sharing
  - express.json: JSON body parser
  - rate_limiter:
      window: 15 minutes
      max_requests: 100
      scope: per IP
  - error_handler: Global error handling

route_specific:
  - authenticate: JWT token verification + active status check
  - authorize: Role-based access control factory
```

---

## Error Handling

```yaml
error_classes:
  AppError:
    base: Error
    fields: [statusCode, message]
  NotFoundError:
    extends: AppError
    status: 404
  UnauthorizedError:
    extends: AppError
    status: 401
  ForbiddenError:
    extends: AppError
    status: 403
  ConflictError:
    extends: AppError
    status: 409

response_formats:
  app_error:
    body: { error: "Error message" }
  validation_error:
    body: { error: "Validation failed", details: [{ field: "name", message: "Required" }] }
  unhandled_error:
    body: { error: "Internal server error" }
```

---

## Validation Schemas (Zod)

```yaml
schemas:
  register:
    email: valid email (required)
    password: min 8 characters (required)
    name: 1-100 characters (required)
  login:
    email: valid email (required)
    password: min 1 character (required)
  create_record:
    amount: positive number (required)
    type: enum [income, expense] (required)
    category: 1-50 characters (required)
    date: YYYY-MM-DD format (required)
    description: max 500 characters (optional)
  update_record:
    all_fields: optional (at least one required)
  pagination:
    page: integer, min 1, default 1
    limit: integer, 1-100, default 20
  filters:
    type: optional enum [income, expense]
    category: optional string
    startDate: optional YYYY-MM-DD
    endDate: optional YYYY-MM-DD
    search: optional string
```

---

## Available Scripts

```yaml
scripts:
  dev: tsx watch src/index.ts          # Start dev server with hot reload
  build: tsc                           # Compile TypeScript to dist/
  start: node dist/index.js            # Run production build
  seed: tsx src/seed.ts                # Populate DB with sample data
  test: vitest run                     # Run all tests once
  test:watch: vitest                   # Run tests in watch mode
```

---

## Seed Data

```yaml
default_users:
  - email: admin@example.com
    password: password123
    role: admin
    status: active
  - email: analyst@example.com
    password: password123
    role: analyst
    status: active
  - email: viewer@example.com
    password: password123
    role: viewer
    status: active

sample_records:
  total_income: 16100
  total_expenses: 5085
  categories:
    income: [Salary, Freelance, Investment, Refund]
    expense: [Rent, Utilities, Groceries, Transport, Entertainment, Healthcare]
```

---

## Key Design Decisions

```yaml
decisions:
  database:
    choice: SQLite over PostgreSQL
    reason: Zero-configuration, synchronous driver, good for single-server
  soft_deletes:
    applies_to: financial_records
    reason: Preserves audit trails for financial data
  jwt_payload:
    includes: Full user profile (minus password)
    tradeoff: Role changes require re-authentication
  architecture:
    style: Flat service layer (plain objects, not classes)
    reason: Simple, maintainable separation from routes
  default_role:
    value: viewer
    promotion: Only admins can promote to analyst or admin
```

---

## API Routes Summary

```yaml
routes:
  health:
    GET /health: Health check (public)
  auth:
    POST /api/auth/register: Register new user (public)
    POST /api/auth/login: Login and get JWT (public)
    GET /api/auth/me: Get current user profile (authenticated)
  users:
    GET /api/users: List all users (admin)
    GET /api/users/:id: Get user by ID (admin)
    PATCH /api/users/:id: Update user (admin)
    DELETE /api/users/:id: Delete user (admin)
  records:
    GET /api/records: List records with filters (authenticated)
    GET /api/records/:id: Get record by ID (authenticated)
    POST /api/records: Create record (admin)
    PATCH /api/records/:id: Update record (admin)
    DELETE /api/records/:id: Soft delete record (admin)
  dashboard:
    GET /api/dashboard/summary: Financial summary (analyst, admin)
    GET /api/dashboard/categories: Category breakdown (analyst, admin)
    GET /api/dashboard/trends/monthly: Monthly trends (analyst, admin)
    GET /api/dashboard/trends/weekly: Weekly trends (analyst, admin)
```
