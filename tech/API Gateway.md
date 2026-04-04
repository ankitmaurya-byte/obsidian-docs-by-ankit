# API Gateway

## What is an API Gateway
```
overview:
  type: Infrastructure component / reverse proxy
  purpose: Single entry point for all client requests to backend services
  analogy: Front desk of a hotel, routes guests to the right room and handles check-in
  layer: Sits between clients and backend microservices

  key_functions:
    - Request routing (route to correct backend service)
    - Authentication and authorization
    - Rate limiting and throttling
    - Load balancing
    - Request/response transformation
    - SSL termination
    - Caching
    - Logging and monitoring
    - Circuit breaking
    - API versioning

  why_needed: |
    In a microservices architecture, clients should not call each service
    directly. An API gateway provides a unified interface, hides internal
    service topology, and centralizes cross-cutting concerns like auth,
    rate limiting, and logging.
```

## How it Works
```
flow:
  1_client_request:
    description: Client sends request to gateway (single URL)
    example: "GET https://api.myapp.com/users/123"

  2_gateway_processes:
    steps:
      - "SSL termination (decrypt HTTPS)"
      - "Authentication (validate JWT/API key)"
      - "Rate limiting (check if client exceeded quota)"
      - "Routing (determine which backend service handles /users)"
      - "Request transformation (add headers, modify path)"
      - "Load balancing (pick a healthy backend instance)"

  3_forward_to_backend:
    description: Gateway forwards request to internal service
    example: "GET http://user-service:3001/users/123"

  4_return_response:
    description: Gateway receives response, optionally transforms it, returns to client
    example: "Add CORS headers, compress response, cache result"

request_routing:
  path_based:
    /users/*: "-> user-service"
    /orders/*: "-> order-service"
    /payments/*: "-> payment-service"
    /auth/*: "-> auth-service"

  header_based:
    "X-API-Version: v2": "-> service-v2"
    "X-API-Version: v1": "-> service-v1"

  method_based:
    "GET /products": "-> product-read-service"
    "POST /products": "-> product-write-service"
```

## Reverse Proxy vs API Gateway
```
comparison:
  reverse_proxy:
    what: Forwards client requests to backend servers
    focus: Load balancing, SSL termination, caching
    examples: Nginx, HAProxy
    features:
      - Load balancing
      - SSL termination
      - Static file serving
      - Basic URL rewriting
      - Health checks
    does_not_have:
      - Built-in authentication
      - Rate limiting with API key awareness
      - Request/response transformation
      - API analytics and developer portal
      - Protocol translation (REST to gRPC)

  api_gateway:
    what: Reverse proxy + API management features
    focus: API lifecycle management, security, observability
    examples: Kong, AWS API Gateway, Traefik, Apigee
    features:
      - Everything a reverse proxy does PLUS
      - Authentication (JWT, OAuth, API keys)
      - Fine-grained rate limiting per consumer
      - Request/response transformation
      - API analytics and logging
      - Developer portal and documentation
      - Circuit breaker and retry policies
      - Protocol translation

  summary: |
    Every API gateway is a reverse proxy, but not every reverse proxy
    is an API gateway. Use Nginx as a reverse proxy for simple setups,
    use Kong/Traefik when you need API management features.
```

## Key Features

### Rate Limiting
```
rate_limiting:
  purpose: Prevent abuse, ensure fair usage, protect backends
  strategies:
    fixed_window:
      description: Count requests in fixed time windows (e.g., per minute)
      example: "100 requests per minute per API key"
      downside: Burst at window boundaries (200 requests in 2 seconds across boundary)

    sliding_window:
      description: Rolling window that smooths out bursts
      example: "Weight current and previous window counts"
      better_than: Fixed window for burst handling

    token_bucket:
      description: Tokens added at steady rate, each request costs one token
      example: "Bucket holds 100 tokens, refills at 10/second"
      allows: Small bursts up to bucket capacity

    leaky_bucket:
      description: Requests processed at fixed rate, excess queued or dropped
      example: "Process 10 requests/second, queue up to 50"
      ensures: Smooth, constant output rate

  response_when_limited:
    status: 429 Too Many Requests
    headers:
      Retry-After: "60"
      X-RateLimit-Limit: "100"
      X-RateLimit-Remaining: "0"
      X-RateLimit-Reset: "1700000060"
```

### Authentication at the Gateway
```
authentication:
  api_key:
    how: Client sends key in header or query param
    header: "X-API-Key: abc123"
    gateway_action: Validate key against database, identify consumer

  jwt_validation:
    how: Client sends JWT in Authorization header
    header: "Authorization: Bearer eyJhbG..."
    gateway_action: Verify signature, check expiration, extract claims
    benefit: No call to auth service needed (stateless)

  oauth_token_introspection:
    how: Gateway sends token to auth server for validation
    used_when: Opaque tokens (not JWTs)
    downside: Extra network call per request

  mutual_tls:
    how: Both client and server present certificates
    used_when: Service-to-service communication, high security

  benefit: |
    Centralizing auth at the gateway means backend services don't need
    to implement auth logic. Gateway validates and passes user info
    (e.g., X-User-ID header) to backends.
```

### Load Balancing
```
load_balancing:
  algorithms:
    round_robin:
      description: Distribute requests to backends in rotation
      best_for: Backends with equal capacity

    weighted_round_robin:
      description: More powerful servers get more requests
      example: "Server A (weight=3) gets 3x more than Server B (weight=1)"

    least_connections:
      description: Send to the backend with fewest active connections
      best_for: Requests with varying processing times

    ip_hash:
      description: Hash client IP to always route to the same backend
      best_for: Session affinity (sticky sessions)
      downside: Uneven distribution if many clients behind same NAT

    random:
      description: Pick a random backend
      surprisingly: Performs well at scale (power of two choices)

  health_checks:
    active: Gateway periodically pings backends (e.g., GET /health)
    passive: Gateway marks backend unhealthy after N consecutive failures
    action: Unhealthy backends removed from rotation until recovered
```

## Popular API Gateways
```
gateways:
  kong:
    type: Open-source API gateway built on Nginx/OpenResty
    written_in: Lua
    features:
      - Plugin ecosystem (auth, rate limiting, logging, transformation)
      - Declarative configuration (YAML/DB)
      - Admin API for dynamic configuration
      - Service mesh support (Kong Mesh)
    deployment: Self-hosted, Docker, Kubernetes
    best_for: Feature-rich API management, plugin ecosystem

  nginx:
    type: Web server / reverse proxy (API gateway with config)
    written_in: C
    features:
      - High performance, low memory
      - Reverse proxy and load balancing
      - SSL termination
      - Rate limiting (basic)
      - Lua scripting via OpenResty for advanced logic
    deployment: Self-hosted, Docker, Kubernetes
    best_for: Simple setups, static routing, high performance

  traefik:
    type: Cloud-native reverse proxy and API gateway
    written_in: Go
    features:
      - Auto-discovery of services (Docker, Kubernetes, Consul)
      - Automatic SSL via Let's Encrypt
      - Middleware chain (auth, rate limit, headers, circuit breaker)
      - Dashboard for monitoring
      - Native Docker and Kubernetes integration
    deployment: Docker, Kubernetes
    best_for: Docker/Kubernetes environments, auto-discovery

  aws_api_gateway:
    type: Managed API gateway (serverless)
    features:
      - REST and WebSocket APIs
      - Lambda integration
      - Usage plans and API keys
      - Request validation
      - Caching
    best_for: AWS-native architectures, serverless

  envoy:
    type: High-performance service proxy
    written_in: C++
    features:
      - L4/L7 proxy
      - gRPC support
      - Advanced load balancing
      - Observability (distributed tracing, metrics)
    used_by: Istio service mesh
    best_for: Service mesh sidecar, gRPC-heavy architectures
```

## Example: Nginx as API Gateway
```
nginx_api_gateway:
  description: |
    Nginx can serve as a lightweight API gateway with routing,
    rate limiting, SSL termination, and basic auth.
```

### Nginx Config as API Gateway
```
# /etc/nginx/nginx.conf

# Define backend service groups
upstream user_service {
    least_conn;
    server 10.0.1.10:3001;
    server 10.0.1.11:3001;
    server 10.0.1.12:3001;
}

upstream order_service {
    server 10.0.2.10:3002;
    server 10.0.2.11:3002;
}

upstream payment_service {
    server 10.0.3.10:3003;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $http_x_api_key zone=per_api_key:10m rate=100r/m;

server {
    listen 443 ssl;
    server_name api.myapp.com;

    # SSL
    ssl_certificate     /etc/ssl/certs/myapp.crt;
    ssl_certificate_key /etc/ssl/private/myapp.key;

    # Global rate limit
    limit_req zone=general burst=20 nodelay;

    # API Key validation (basic)
    # In production, use Lua/OpenResty or auth_request to validate against a DB
    if ($http_x_api_key = "") {
        return 401 '{"error": "API key required"}';
    }

    # Route: /api/users -> user_service
    location /api/users {
        proxy_pass http://user_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Route: /api/orders -> order_service
    location /api/orders {
        proxy_pass http://order_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Route: /api/payments -> payment_service (stricter rate limit)
    location /api/payments {
        limit_req zone=per_api_key burst=5 nodelay;
        proxy_pass http://payment_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check endpoint
    location /health {
        return 200 '{"status": "ok"}';
        add_header Content-Type application/json;
    }

    # Block everything else
    location / {
        return 404 '{"error": "not found"}';
        add_header Content-Type application/json;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.myapp.com;
    return 301 https://$host$request_uri;
}
```

## Tags
```
tags:
  - api-gateway
  - reverse-proxy
  - rate-limiting
  - load-balancing
  - authentication
  - microservices
  - kong
  - nginx
  - traefik
  - routing
```
