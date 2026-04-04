# Load Balancing

## What is Load Balancing
```
overview:
  definition: |
    Load balancing distributes incoming network traffic across
    multiple backend servers to ensure no single server is
    overwhelmed, improving availability and responsiveness.
  purpose:
    - Distribute traffic evenly across servers
    - Improve application availability and reliability
    - Enable horizontal scaling (add more servers)
    - Provide fault tolerance (route around failed servers)
    - Enable zero-downtime deployments

  analogy: |
    Like a restaurant host seating customers across all tables
    instead of sending everyone to the same waiter.
```

## Load Balancing Algorithms
```
algorithms:

  round_robin:
    description: Distribute requests sequentially across servers
    how: "Request 1 -> Server A, Request 2 -> Server B, Request 3 -> Server C, repeat"
    pros:
      - Simple to implement
      - Even distribution if servers are identical
    cons:
      - Ignores server load and capacity
      - Bad if servers have different specs
    best_for: Identical servers with similar request costs

  weighted_round_robin:
    description: Round robin but servers have weights based on capacity
    how: "Server A (weight 3) gets 3x more requests than Server C (weight 1)"
    pros:
      - Accounts for different server capacities
    cons:
      - Weights are static, don't adapt to real-time load
    best_for: Heterogeneous server fleet

  least_connections:
    description: Send to server with fewest active connections
    how: "Track active connections per server, route to lowest count"
    pros:
      - Adapts to real-time load
      - Handles variable request durations well
    cons:
      - Slightly more overhead (tracking connections)
    best_for: Long-lived connections, varying request durations

  weighted_least_connections:
    description: Least connections weighted by server capacity
    how: "Route to server with lowest (active_connections / weight) ratio"
    best_for: Heterogeneous servers with variable request durations

  ip_hash:
    description: Hash client IP to determine server (same client always goes to same server)
    how: "server = hash(client_ip) % num_servers"
    pros:
      - Ensures session persistence without cookies
      - Simple client affinity
    cons:
      - Uneven distribution if IP ranges are clustered
      - Adding/removing servers reshuffles many clients
    best_for: Stateful applications needing session affinity

  consistent_hashing:
    description: Hash ring that minimizes remapping when servers are added/removed
    how: |
      1. Place servers on a hash ring (virtual nodes)
      2. Hash the request key (IP, user ID)
      3. Walk clockwise on ring to find nearest server
      4. Adding/removing server only affects adjacent keys
    pros:
      - Minimal disruption when scaling up/down
      - Good load distribution with virtual nodes
    cons:
      - More complex to implement
    best_for: Caching layers, distributed systems, CDNs

  random:
    description: Randomly pick a server
    pros: Simple, no state needed
    cons: Can be uneven with small server counts
    best_for: Large server pools where statistical distribution is good enough

  least_response_time:
    description: Route to server with fastest average response time + fewest connections
    pros: Optimizes for user-perceived performance
    cons: Requires continuous health monitoring
    best_for: Performance-sensitive applications
```

## L4 vs L7 Load Balancing
```
layers:

  l4_transport_layer:
    operates_on: TCP/UDP packets
    sees: Source IP, destination IP, ports
    does_not_see: HTTP headers, URLs, cookies, request body
    how: Forwards TCP connections based on IP and port
    performance: Very fast (no packet inspection)
    use_cases:
      - Raw TCP/UDP traffic
      - Database connections
      - Non-HTTP protocols
      - When performance is critical
    tools:
      - AWS NLB (Network Load Balancer)
      - HAProxy (TCP mode)
      - Nginx (stream module)
      - Linux IPVS / LVS

  l7_application_layer:
    operates_on: HTTP/HTTPS requests
    sees: URLs, headers, cookies, request body, method
    how: Inspects HTTP content and makes routing decisions
    performance: Slower than L4 (must parse HTTP)
    capabilities:
      - Route by URL path (/api -> backend-api, /web -> backend-web)
      - Route by host header (api.example.com vs www.example.com)
      - Route by cookie or header (A/B testing, canary deploys)
      - SSL/TLS termination
      - Request/response modification
      - Compression, caching
    use_cases:
      - Web applications and APIs
      - Microservices routing
      - A/B testing and canary deployments
      - SSL termination
    tools:
      - AWS ALB (Application Load Balancer)
      - Nginx (http module)
      - HAProxy (http mode)
      - Envoy
      - Traefik
      - Caddy

  comparison:
    speed: "L4 > L7 (less processing)"
    intelligence: "L7 > L4 (content-aware routing)"
    ssl_termination: "L7 (L4 passes encrypted traffic through)"
    websockets: "Both support, L7 can inspect upgrade headers"
    recommendation: "Use L7 for HTTP/HTTPS, L4 for everything else"
```

## Health Checks
```
health_checks:
  description: Load balancer periodically checks if backend servers are healthy

  types:
    passive:
      description: Monitor responses from normal traffic
      how: "If server returns 5xx or times out, mark unhealthy"
      pros: No extra traffic
      cons: Only detects failures after real users are affected

    active:
      description: Send periodic probe requests to health endpoint
      how: "GET /health every 10 seconds, expect 200 OK"
      pros: Detects failures before users are affected
      cons: Extra traffic to backends

  health_endpoint:
    simple: "GET /health -> 200 OK"
    detailed: |
      GET /health -> 200 OK
      {
        "status": "healthy",
        "checks": {
          "database": "ok",
          "redis": "ok",
          "disk_space": "ok"
        },
        "uptime": "72h15m"
      }

  parameters:
    interval: "How often to check (e.g., every 10 seconds)"
    timeout: "How long to wait for response (e.g., 5 seconds)"
    healthy_threshold: "Consecutive successes to mark healthy (e.g., 2)"
    unhealthy_threshold: "Consecutive failures to mark unhealthy (e.g., 3)"

  behavior_on_failure:
    - "Remove server from rotation (stop sending traffic)"
    - "Continue checking at interval"
    - "Re-add when healthy threshold met"
    - "Optionally drain existing connections gracefully"
```

## Session Affinity
```
session_affinity:
  also_called: Sticky sessions
  description: Ensure requests from same client always go to same backend server

  why_needed:
    - Server stores session state in memory (not shared)
    - WebSocket connections need to stay on same server
    - Shopping cart stored in server memory

  methods:
    cookie_based:
      how: "Load balancer sets cookie (e.g., SERVERID=backend1)"
      pros: Works even if client IP changes
      example: "Set-Cookie: SERVERID=backend-2; Path=/; HttpOnly"

    ip_based:
      how: "Hash client IP to pick server"
      pros: No cookie needed
      cons: Breaks with NAT, proxies, mobile networks

    header_based:
      how: "Route based on custom header (e.g., X-Session-ID)"
      pros: Flexible, works in API scenarios

  better_alternative: |
    Avoid sticky sessions by storing session state externally:
    - Redis for session data
    - JWT tokens (stateless sessions)
    - Database-backed sessions
    This allows any server to handle any request.
```

## Popular Load Balancers
```
tools:

  nginx:
    type: Software (L4 + L7)
    description: Most popular web server and reverse proxy
    features:
      - HTTP and TCP/UDP load balancing
      - SSL termination
      - Caching, compression
      - Rate limiting
      - Free and Nginx Plus (commercial)
    best_for: Web applications, reverse proxy, all-in-one solution

  haproxy:
    type: Software (L4 + L7)
    description: High-performance TCP/HTTP load balancer
    features:
      - Very fast and lightweight
      - Advanced health checking
      - Detailed stats dashboard
      - ACL-based routing
    best_for: High-performance environments, complex routing rules

  envoy:
    type: Software (L4 + L7)
    description: Cloud-native edge/service proxy
    features:
      - Built for microservices (service mesh sidecar)
      - gRPC native support
      - Observability built-in (stats, tracing, logging)
      - Dynamic configuration via xDS API
    best_for: Kubernetes, service mesh (Istio uses Envoy)

  traefik:
    type: Software (L7)
    description: Cloud-native reverse proxy with auto-discovery
    features:
      - Auto-discovers services from Docker, K8s, Consul
      - Automatic HTTPS with Let's Encrypt
      - Dashboard UI
      - Middleware (auth, rate limiting, circuit breaker)
    best_for: Docker and Kubernetes environments

  aws_alb:
    type: Managed (L7)
    description: AWS Application Load Balancer
    features:
      - HTTP/HTTPS and gRPC
      - Path and host-based routing
      - Native integration with ECS, Lambda, EC2
      - WAF integration
    best_for: AWS-hosted web applications

  aws_nlb:
    type: Managed (L4)
    description: AWS Network Load Balancer
    features:
      - Ultra-low latency (millions of requests/sec)
      - Static IP / Elastic IP support
      - TCP, UDP, TLS
      - Preserves source IP
    best_for: TCP/UDP workloads, gaming, IoT on AWS
```

## Example - Nginx Load Balancer Config
```
nginx_config:
  file: /etc/nginx/nginx.conf
  config: |
    http {
        # Define upstream backend servers
        upstream backend_api {
            # Least connections algorithm
            least_conn;

            # Backend servers with weights
            server 10.0.1.10:8080 weight=3;
            server 10.0.1.11:8080 weight=2;
            server 10.0.1.12:8080 weight=1;

            # Backup server (used only when others are down)
            server 10.0.1.13:8080 backup;

            # Health check parameters
            # max_fails: mark unhealthy after N failures
            # fail_timeout: time window for max_fails + how long to wait before retry
            server 10.0.1.10:8080 max_fails=3 fail_timeout=30s;
        }

        upstream backend_web {
            # IP hash for session affinity
            ip_hash;

            server 10.0.2.10:3000;
            server 10.0.2.11:3000;
            server 10.0.2.12:3000;
        }

        # Rate limiting zone
        limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

        server {
            listen 80;
            server_name example.com;

            # Redirect HTTP to HTTPS
            return 301 https://$host$request_uri;
        }

        server {
            listen 443 ssl;
            server_name example.com;

            ssl_certificate /etc/ssl/certs/example.com.crt;
            ssl_certificate_key /etc/ssl/private/example.com.key;

            # API routes -> backend_api
            location /api/ {
                limit_req zone=api_limit burst=20 nodelay;

                proxy_pass http://backend_api;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;

                # Timeouts
                proxy_connect_timeout 5s;
                proxy_read_timeout 30s;
                proxy_send_timeout 10s;
            }

            # Web routes -> backend_web
            location / {
                proxy_pass http://backend_web;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;

                # WebSocket support
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
            }

            # Health check endpoint
            location /health {
                access_log off;
                return 200 'OK';
                add_header Content-Type text/plain;
            }
        }
    }
```

## Example - Health Check Endpoint in Go
```go
package main

import (
    "context"
    "encoding/json"
    "net/http"
    "time"

    "github.com/redis/go-redis/v9"
    "github.com/jackc/pgx/v5/pgxpool"
)

type HealthStatus struct {
    Status  string            `json:"status"`
    Checks  map[string]string `json:"checks"`
    Uptime  string            `json:"uptime"`
}

var (
    startTime = time.Now()
    db        *pgxpool.Pool
    rdb       *redis.Client
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
    defer cancel()

    checks := map[string]string{}
    healthy := true

    // Check database
    if err := db.Ping(ctx); err != nil {
        checks["database"] = "unhealthy: " + err.Error()
        healthy = false
    } else {
        checks["database"] = "ok"
    }

    // Check Redis
    if err := rdb.Ping(ctx).Err(); err != nil {
        checks["redis"] = "unhealthy: " + err.Error()
        healthy = false
    } else {
        checks["redis"] = "ok"
    }

    status := HealthStatus{
        Status:  "healthy",
        Checks:  checks,
        Uptime:  time.Since(startTime).Round(time.Second).String(),
    }

    if !healthy {
        status.Status = "unhealthy"
        w.WriteHeader(http.StatusServiceUnavailable)
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(status)
}

// Liveness: is the process alive (for K8s liveness probe)
func livenessHandler(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("OK"))
}

// Readiness: is the process ready to accept traffic (for K8s readiness probe)
func readinessHandler(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
    defer cancel()

    if err := db.Ping(ctx); err != nil {
        http.Error(w, "not ready", http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("READY"))
}

func main() {
    http.HandleFunc("/health", healthHandler)
    http.HandleFunc("/healthz", livenessHandler)
    http.HandleFunc("/readyz", readinessHandler)
    http.ListenAndServe(":8080", nil)
}
```

## Best Practices
```
best_practices:
  architecture:
    - "Use L7 for HTTP traffic, L4 for TCP/UDP and non-HTTP protocols"
    - "Always configure health checks (active preferred)"
    - "Avoid sticky sessions - externalize state to Redis/DB instead"
    - "Use consistent hashing for cache-tier load balancing"
    - "Deploy load balancers in pairs for high availability"

  configuration:
    - "Set appropriate timeouts (connect, read, write)"
    - "Enable connection draining during server removal"
    - "Configure proper X-Forwarded-For and X-Real-IP headers"
    - "Rate limit at the load balancer level as first defense"
    - "Enable access logging for debugging and analytics"

  scaling:
    - "Start with round robin, move to least connections as traffic grows"
    - "Use weighted algorithms when servers have different capacities"
    - "Auto-scale backend servers based on load metrics"
    - "Use DNS-based load balancing across regions for global distribution"

  security:
    - "Terminate SSL/TLS at the load balancer"
    - "Only allow load balancer IPs to reach backend servers"
    - "Use WAF integration (AWS WAF, Cloudflare) for attack mitigation"
    - "Keep backends on private subnets, only LB on public"
```

## Tags
```
tags:
  - load-balancing
  - nginx
  - infrastructure
  - scaling
  - system-design
  - high-availability
```
