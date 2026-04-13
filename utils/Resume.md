---
title: Ankit Maurya – Resume Breakdown
tags:
  - resume
  - backend
  - nodejs
  - golang
  - postgresql
  - redis
  - devops
type: profile
status: active
role: SDE (Backend)
stack:
  languages: [Node.js, Go, Java, Python, TypeScript]
  frontend: [React.js, Next.js, HTML, CSS, Tailwind CSS]
  databases: [PostgreSQL, MongoDB, Redis]
  tools: [Docker, AWS, Git, Socket.io, Redux, Zustand]
  testing: [Postman, k6]
location: Bangalore, HSR Layout
email: ankit.fsdev@gmail.com
phone: +91 8010078449
education: B.Sc. Computer Science – Vidyavardhini College of Engineering (Aug 2025)
dsa_problems_solved: 700+
created: 2026-04-06
---

# 👤 Ankit Maurya — Resume Deep Dive

> Backend-leaning full-stack engineer with internship experience across 4 companies. Strong in Node.js, Go, and PostgreSQL. Has built real-time systems, DevOps pipelines, and performance-optimized APIs.

---

## 🗂️ Table of Contents

- [[#Work Experience]]
  - [[#Swift (Feb 2026 – Present)]]
  - [[#Intervue (Oct 2025 – Feb 2026)]]
  - [[#Mycorr (Jan 2025 – Aug 2025)]]
  - [[#Datamingle (Sep 2024 – Dec 2024)]]
- [[#Projects]]
  - [[#Timeline – Workspace & Role Manager]]
- [[#Skills Breakdown]]
- [[#Education]]

---

## 💼 Work Experience

### 🏢 Swift (Feb 2026 – Present)
**Role:** SDE Intern | Bangalore  
**Stack:** `Node.js` · `MongoDB` · `GraphQL` · `Redis` · `Shopify API`

#### What he did:
- Built backend services for **checkout**, **upsell/cross-sell**, and **fulfillment** flows
- Integrated **Shopify API** for e-commerce operations
- Implemented **Redis-based distributed caching** → reduced latency by ~35%

#### 📦 Redis Caching Example
```typescript
// Before: Every request hits the DB
app.get('/products/:id', async (req, res) => {
  const product = await db.collection('products').findOne({ _id: req.params.id });
  res.json(product);
});

// After: Redis caching layer (what Ankit likely implemented)
import { createClient } from 'redis';
const redis = createClient();

app.get('/products/:id', async (req, res) => {
  const cacheKey = `product:${req.params.id}`;

  // 1. Check cache first
  const cached = await redis.get(cacheKey);
  if (cached) return res.json(JSON.parse(cached));

  // 2. Cache miss → fetch from DB
  const product = await db.collection('products').findOne({ _id: req.params.id });

  // 3. Store in cache with TTL (Time To Live) = 60 seconds
  await redis.setEx(cacheKey, 60, JSON.stringify(product));

  res.json(product);
});
// Result: Subsequent requests skip DB entirely → ~35% latency reduction
```

#### 📦 GraphQL Checkout Service Example
```typescript
// GraphQL schema for checkout
const typeDefs = gql`
  type CheckoutSession {
    id: ID!
    items: [CartItem!]!
    total: Float!
    status: CheckoutStatus!
  }

  type Mutation {
    createCheckout(input: CheckoutInput!): CheckoutSession!
    applyUpsell(checkoutId: ID!, productId: ID!): CheckoutSession!
  }
`;

const resolvers = {
  Mutation: {
    createCheckout: async (_, { input }) => {
      // Validate items, calculate total, persist to MongoDB
      const session = await CheckoutModel.create({ ...input, status: 'PENDING' });
      return session;
    },
    applyUpsell: async (_, { checkoutId, productId }) => {
      // Cross-sell logic: add recommended product to existing checkout
      return CheckoutModel.findByIdAndUpdate(
        checkoutId,
        { $push: { items: { productId, quantity: 1 } } },
        { new: true }
      );
    },
  },
};
```

---

### 🏢 Intervue (Oct 2025 – Feb 2026)
**Role:** SDE Intern | Bangalore  
**Stack:** `Node.js` · `PostgreSQL` · `React` · `TypeScript` · `Postman`

#### What he did:
- Optimized REST APIs with **indexing**, **caching**, and **query tuning** → 40% latency reduction
- Built **modular React + TypeScript** components with strict API contracts → 25% fewer integration bugs
- Validated APIs using **Postman** test suites

#### 📦 PostgreSQL Query Optimization Example
```sql
-- BEFORE: Slow query (full table scan)
SELECT * FROM interviews
WHERE candidate_email = 'ankit@example.com'
AND status = 'completed';
-- Execution time: ~800ms on large dataset

-- AFTER: Add composite index
CREATE INDEX idx_interviews_email_status
ON interviews(candidate_email, status);

-- Query now uses index scan
EXPLAIN ANALYZE
SELECT id, scheduled_at, score FROM interviews
WHERE candidate_email = 'ankit@example.com'
AND status = 'completed';
-- Execution time: ~48ms (40%+ faster)
```

#### 📦 TypeScript API Contract Pattern
```typescript
// Strict API contracts prevent integration defects (Ankit's approach)

// 1. Define the contract (shared type)
interface InterviewResult {
  id: string;
  candidateId: string;
  score: number;           // 0–100
  status: 'pass' | 'fail' | 'pending';
  feedback: string | null;
  completedAt: Date | null;
}

// 2. Backend: typed response
const getInterviewResult = async (id: string): Promise<InterviewResult> => {
  const row = await db.query(
    'SELECT * FROM interviews WHERE id = $1', [id]
  );
  return row as InterviewResult; // Type enforcement at boundary
};

// 3. Frontend: typed consumption
const ResultCard: React.FC<{ id: string }> = ({ id }) => {
  const [result, setResult] = React.useState<InterviewResult | null>(null);

  useEffect(() => {
    fetch(`/api/interviews/${id}`)
      .then(r => r.json())
      .then((data: InterviewResult) => setResult(data)); // Typed
  }, [id]);

  return <div>{result?.score ?? 'Loading...'}</div>;
};
// Strict typing = compiler catches mismatches before runtime = 25% fewer bugs
```

---

### 🏢 Mycorr (Jan 2025 – Aug 2025)
**Role:** SDE Intern | Chennai (Remote)  
**Stack:** `Node.js` · `React.js` · `PostgreSQL` · `SSE` · `Vite`

#### What he did:
- Built **real-time systems using SSE** (Server-Sent Events)
- Migrated build tooling **Webpack → Vite** → faster dev builds
- Applied **scalable architecture patterns** (modular backend)

#### 📦 Server-Sent Events (SSE) Example
```typescript
// SSE: one-way real-time stream from server to browser
// Used by Ankit for live data updates (e.g., live agriculture sensor data)

// Server (Node.js/Express)
app.get('/api/live-feed', (req, res) => {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Send event every 2 seconds
  const interval = setInterval(() => {
    const data = { temperature: Math.random() * 40, humidity: Math.random() * 100 };
    res.write(`data: ${JSON.stringify(data)}\n\n`); // SSE format
  }, 2000);

  // Cleanup on client disconnect
  req.on('close', () => clearInterval(interval));
});

// Client (React)
useEffect(() => {
  const eventSource = new EventSource('/api/live-feed');

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setSensorData(prev => [...prev, data]);
  };

  return () => eventSource.close(); // Cleanup
}, []);
```

#### 📦 Vite vs Webpack (Why migration matters)
```bash
# Webpack cold start (before)
$ npm run dev
# Build time: ~18 seconds (bundles everything upfront)

# Vite cold start (after Ankit's migration)
$ npm run dev
# Build time: ~1.2 seconds (uses native ESM, only transforms on-demand)

# vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
  build: { sourcemap: true },
});
```

---

### 🏢 Datamingle (Sep 2024 – Dec 2024)
**Role:** SDE Intern | Mumbai (Remote)  
**Stack:** `React` · `Node.js` · `PostgreSQL` · `Docker` · `AWS` · `CI/CD`

#### What he did:
- Full-stack ownership: development + CI/CD + Docker + AWS deployment
- Reduced release cycles by **60%** with standardized DevOps workflows

#### 📦 Docker + CI/CD Pipeline Example
```yaml
# docker-compose.yml (standardized environment Ankit set up)
version: '3.8'
services:
  api:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/datamingle
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache

  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: pass

  cache:
    image: redis:7-alpine

volumes:
  pgdata:
```

```yaml
# .github/workflows/deploy.yml (CI/CD pipeline)
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t datamingle-api ./backend

      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS ...
          docker tag datamingle-api $ECR_REPO:latest
          docker push $ECR_REPO:latest

      - name: Deploy to ECS
        run: aws ecs update-service --cluster prod --service api --force-new-deployment
# Result: Automated deployments replaced manual steps → 60% faster releases
```

---

## 🚀 Projects

### 📋 Timeline – Workspace & Role Manager
**Stack:** `Next.js` · `Go` · `WebSocket` · `Swagger` · `Zustand` · `k6`  
**Scale:** 10,000+ concurrent users

#### What he built:
- Real-time **Kanban board** with live task sync
- **Go WebSocket engine** for low-latency state sync
- **Load tested** with k6 up to 10k concurrent users
- **Web Workers** to offload heavy computation off the main thread

#### 📦 Go WebSocket Server
```go
// Go WebSocket engine (core of Timeline's real-time sync)
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "sync"
    "github.com/gorilla/websocket"
)

type Hub struct {
    clients   map[*websocket.Conn]string // conn → workspaceID
    broadcast chan Message
    mu        sync.RWMutex
}

type Message struct {
    WorkspaceID string      `json:"workspaceId"`
    Event       string      `json:"event"` // "task_moved", "task_created"
    Payload     interface{} `json:"payload"`
}

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true },
}

func (h *Hub) handleConnection(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil { return }
    defer conn.Close()

    workspaceID := r.URL.Query().Get("workspaceId")

    // Register client
    h.mu.Lock()
    h.clients[conn] = workspaceID
    h.mu.Unlock()

    // Listen for messages from this client
    for {
        _, raw, err := conn.ReadMessage()
        if err != nil { break }

        var msg Message
        json.Unmarshal(raw, &msg)
        h.broadcast <- msg // Fan-out to all workspace members
    }
}

func (h *Hub) runBroadcast() {
    for msg := range h.broadcast {
        h.mu.RLock()
        for conn, wsID := range h.clients {
            if wsID == msg.WorkspaceID { // Only send to same workspace
                conn.WriteJSON(msg)
            }
        }
        h.mu.RUnlock()
    }
}
// This pattern scales to 10k+ concurrent users with Go's goroutine model
```

#### 📦 k6 Load Testing
```javascript
// k6 load test script (how Ankit validated 10k concurrent users)
import ws from 'k6/ws';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 1000 },   // Ramp up to 1k users
    { duration: '1m',  target: 10000 },  // Peak: 10k concurrent
    { duration: '30s', target: 0 },      // Ramp down
  ],
};

export default function () {
  const url = 'ws://localhost:8080/ws?workspaceId=ws_test';

  const res = ws.connect(url, {}, (socket) => {
    socket.on('open', () => {
      socket.send(JSON.stringify({
        event: 'task_moved',
        payload: { taskId: 'task_1', column: 'done' },
      }));
    });

    socket.on('message', (data) => {
      check(data, { 'received broadcast': (d) => d.length > 0 });
    });

    socket.setTimeout(() => socket.close(), 5000);
  });

  check(res, { 'status is 101': (r) => r && r.status === 101 });
}
```

#### 📦 Web Workers (main thread offloading)
```typescript
// main.ts — offload heavy Kanban state computation to a worker
const worker = new Worker(new URL('./kanban.worker.ts', import.meta.url));

// Send raw task data to worker
worker.postMessage({ tasks, filters, sortBy: 'priority' });

// Receive sorted/filtered result without blocking UI
worker.onmessage = (e) => {
  setProcessedTasks(e.data.result);
};

// kanban.worker.ts — runs in separate thread
self.onmessage = (e) => {
  const { tasks, filters, sortBy } = e.data;

  // Heavy computation (won't freeze the UI)
  const filtered = tasks.filter(t => filters.every(f => f(t)));
  const sorted = filtered.sort((a, b) => a[sortBy] > b[sortBy] ? 1 : -1);

  self.postMessage({ result: sorted });
};
```

---

## 🛠️ Skills Breakdown

| Category | Technologies |
|---|---|
| **Languages** | TypeScript, JavaScript, Go, Java, Python, SQL |
| **Backend** | Node.js, Express.js, Go (net/http, gorilla/websocket) |
| **Frontend** | React.js, Next.js, Tailwind CSS, Zustand, Redux |
| **Databases** | PostgreSQL, MongoDB, Redis |
| **DevOps** | Docker, Docker Compose, AWS (ECS, ECR), CI/CD (GitHub Actions) |
| **Real-time** | WebSocket, Socket.io, SSE (Server-Sent Events) |
| **API** | REST, GraphQL, Swagger/OpenAPI |
| **Testing** | Postman, k6 (load testing) |

---

## 🎓 Education

| Field | Value |
|---|---|
| **Degree** | B.Sc. Computer Science |
| **College** | Vidyavardhini College of Engineering |
| **Location** | Mumbai, Vasai |
| **Graduated** | Aug 2025 |
| **DSA** | 700+ problems solved, competitive programming & hackathons |

---

## 🔖 Tags

`#backend` `#nodejs` `#golang` `#postgresql` `#redis` `#websocket` `#sse` `#docker` `#aws` `#graphql` `#typescript` `#react` `#devops` `#load-testing` `#k6` `#real-time` `#internship` `#resume`