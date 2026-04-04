# Nginx

## What is Nginx
```
overview:
  full_name: Nginx (pronounced "engine-x")
  type: Web server, reverse proxy, load balancer, HTTP cache
  written_in: C
  created_by: Igor Sysoev (2004)
  license: BSD-like (open source), Nginx Plus (commercial)
  architecture: Event-driven, asynchronous, non-blocking
  default_port: 80 (HTTP), 443 (HTTPS)

  key_features:
    - High performance (handles 10,000+ concurrent connections)
    - Low memory footprint
    - Reverse proxy with load balancing
    - SSL/TLS termination
    - Static file serving
    - HTTP caching
    - Rate limiting
    - Gzip compression
    - URL rewriting
    - WebSocket proxying
    - HTTP/2 and HTTP/3 support

  architecture_detail:
    master_process: Reads config, manages worker processes
    worker_processes: Handle actual requests (typically 1 per CPU core)
    event_loop: Each worker uses epoll/kqueue to handle thousands of connections
    non_blocking: Workers never block on I/O, can handle many connections simultaneously
    vs_apache: Apache uses thread/process per connection, Nginx uses event loop
```

## When to Use Nginx
```
use_cases:
  reverse_proxy:
    description: Sit in front of application servers, forward requests
    why: Decouple clients from backend, add security layer
    example: Nginx on port 80/443, proxies to Go app on port 8080

  load_balancer:
    description: Distribute traffic across multiple backend servers
    why: Horizontal scaling, high availability
    example: 3 app servers behind Nginx with least_conn

  static_file_server:
    description: Serve HTML, CSS, JS, images directly
    why: Much faster than serving static files through an application server
    example: Serve React build from /var/www/html

  ssl_termination:
    description: Handle HTTPS at Nginx, forward plain HTTP to backends
    why: Centralize certificate management, offload TLS from app servers
    example: Let's Encrypt certs on Nginx, proxy_pass to http://backend

  api_gateway:
    description: Route API requests to different microservices
    why: Single entry point, centralized auth and rate limiting
    example: /api/users -> user-service, /api/orders -> order-service

  caching:
    description: Cache backend responses to reduce load
    why: Avoid hitting the backend for repeated identical requests
    example: Cache GET /api/products for 60 seconds
```

## Nginx vs Apache
```
comparison:
  nginx:
    architecture: Event-driven, async, non-blocking
    concurrency: Handles 10,000+ connections with low memory
    static_files: Extremely fast (serves directly)
    config_style: Centralized config files (nginx.conf)
    dynamic_content: Proxies to app servers (FastCGI, proxy_pass)
    .htaccess: Not supported (all config in main files)
    modules: Compiled at build time (dynamic modules since 1.9.11)
    memory_per_connection: Very low (~2.5MB per 1000 connections)
    best_for: Reverse proxy, load balancing, high concurrency, static serving

  apache:
    architecture: Process/thread per connection (prefork, worker, event MPMs)
    concurrency: Lower under high load (more memory per connection)
    static_files: Slower than Nginx
    config_style: ".htaccess per-directory overrides"
    dynamic_content: Built-in module support (mod_php, mod_python)
    .htaccess: Supported (convenient but slower due to per-request file checks)
    modules: Dynamically loaded at runtime
    memory_per_connection: Higher (~10MB per connection with prefork)
    best_for: Shared hosting, .htaccess needs, embedded language processing

  common_pattern: |
    Use both: Nginx as reverse proxy in front of Apache.
    Nginx handles static files, SSL, and load balancing.
    Apache handles dynamic content with mod_php.
```

## Core Configuration

### Config File Structure
```
config_structure:
  main_config: /etc/nginx/nginx.conf
  site_configs: /etc/nginx/conf.d/*.conf or /etc/nginx/sites-available/*
  default_log: /var/log/nginx/access.log and error.log

  hierarchy:
    main_context:
      description: Global settings (worker processes, error log)
    events_block:
      description: Connection handling settings (worker_connections)
    http_block:
      description: HTTP server settings (contains server blocks)
    server_block:
      description: Virtual host configuration (listen, server_name)
    location_block:
      description: Request URI matching and handling
    upstream_block:
      description: Backend server groups for load balancing

  directive_inheritance: |
    Directives set in outer blocks are inherited by inner blocks
    unless overridden. http -> server -> location
```

### Basic Server Config
```
# Serve a static website
server {
    listen 80;
    server_name mysite.com www.mysite.com;

    root /var/www/mysite;
    index index.html;

    # Serve static files directly
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }

    error_page 404 /404.html;
}
```

## Reverse Proxy

### proxy_pass
```
proxy_pass_explained:
  what: Forwards client requests to a backend server
  directive: proxy_pass
  context: location block

  basic_usage: |
    location /api {
        proxy_pass http://localhost:8080;
    }
    # Request: /api/users -> backend receives /api/users

  trailing_slash_matters: |
    # WITHOUT trailing slash in proxy_pass:
    location /api {
        proxy_pass http://localhost:8080;
    }
    # /api/users -> http://localhost:8080/api/users (path preserved)

    # WITH trailing slash in proxy_pass:
    location /api/ {
        proxy_pass http://localhost:8080/;
    }
    # /api/users -> http://localhost:8080/users (prefix stripped)

  important_headers: |
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
```

### Reverse Proxy Config
```
# Reverse proxy for a Go/Node.js application
server {
    listen 80;
    server_name app.mysite.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;

        # Pass real client info to backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Load Balancing

### Upstream Blocks
```
upstream_explained:
  what: Defines a group of backend servers for load balancing
  directive: upstream
  context: http block
  used_with: proxy_pass http://upstream_name;
```

### Load Balancing Algorithms
```
# Round Robin (default) - distribute evenly in rotation
upstream backend_round_robin {
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080;
}

# Weighted Round Robin - more traffic to powerful servers
upstream backend_weighted {
    server 10.0.1.10:8080 weight=5;   # gets 5x the traffic
    server 10.0.1.11:8080 weight=3;   # gets 3x the traffic
    server 10.0.1.12:8080 weight=1;   # baseline
}

# Least Connections - send to server with fewest active connections
upstream backend_least_conn {
    least_conn;
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080;
}

# IP Hash - same client IP always goes to same server (sticky sessions)
upstream backend_ip_hash {
    ip_hash;
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080;
}

# Server options
upstream backend_with_options {
    least_conn;
    server 10.0.1.10:8080 weight=3;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080 backup;           # only used when others are down
    server 10.0.1.13:8080 down;             # marked as permanently offline
    server 10.0.1.14:8080 max_fails=3 fail_timeout=30s;  # health check
}

# Use the upstream
server {
    listen 80;
    server_name app.mysite.com;

    location / {
        proxy_pass http://backend_least_conn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```
load_balancing_summary:
  round_robin:
    description: Default, rotate through servers one by one
    best_for: Servers with equal capacity, stateless apps
    sticky: No

  weighted_round_robin:
    description: Servers with higher weight get more requests
    best_for: Mixed-capacity servers
    sticky: No

  least_connections:
    description: Pick server with fewest active connections
    best_for: Requests with varying processing times
    sticky: No

  ip_hash:
    description: Hash client IP to always reach same server
    best_for: Session affinity without external session store
    sticky: Yes
    downside: Uneven distribution if many clients behind NAT
```

## SSL Termination
```
ssl_termination:
  what: Nginx handles HTTPS, forwards plain HTTP to backends
  benefit: Centralize cert management, offload crypto from app servers
```

### SSL Config
```
# HTTPS with SSL termination
server {
    listen 443 ssl http2;
    server_name mysite.com;

    # Certificates (e.g., from Let's Encrypt)
    ssl_certificate     /etc/letsencrypt/live/mysite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mysite.com/privkey.pem;

    # SSL settings (modern config)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS (force HTTPS for 1 year)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    location / {
        proxy_pass http://localhost:8080;  # plain HTTP to backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name mysite.com;
    return 301 https://$host$request_uri;
}
```

## Rate Limiting
```
rate_limiting:
  directives:
    limit_req_zone: Define a shared memory zone and rate
    limit_req: Apply rate limit to a location
  algorithm: Leaky bucket

  parameters:
    zone: "Shared memory zone name and size"
    rate: "Allowed request rate (e.g., 10r/s or 60r/m)"
    burst: "Number of excess requests to queue"
    nodelay: "Process burst requests immediately instead of spacing them"
```

### Rate Limiting Config
```
# Define rate limit zones (in http block)
limit_req_zone $binary_remote_addr zone=ip_limit:10m rate=10r/s;
limit_req_zone $http_x_api_key zone=api_key_limit:10m rate=100r/m;

server {
    listen 80;
    server_name api.mysite.com;

    # Apply rate limit per IP (10 requests/second, burst of 20)
    location /api/ {
        limit_req zone=ip_limit burst=20 nodelay;
        limit_req_status 429;

        proxy_pass http://localhost:8080;
    }

    # Stricter limit for expensive endpoints
    location /api/search {
        limit_req zone=ip_limit burst=5 nodelay;
        limit_req_status 429;

        proxy_pass http://localhost:8080;
    }
}
```

```
rate_limit_explanation:
  "rate=10r/s burst=20 nodelay":
    meaning: |
      - Allow 10 requests per second sustained
      - Allow bursts up to 20 requests
      - Process burst requests immediately (don't queue)
      - Reject requests beyond burst with 429

  "rate=1r/s burst=5":
    meaning: |
      - Allow 1 request per second sustained
      - Queue up to 5 excess requests (delayed processing)
      - Reject requests beyond 5 in queue with 503 (or custom status)

  zone_sizing: |
    10m (10 megabytes) stores ~160,000 IP addresses
    Adjust based on expected unique client count
```

## Static File Serving
```
# Serve static files (React/Vue/Angular build)
server {
    listen 80;
    server_name mysite.com;

    root /var/www/mysite/build;
    index index.html;

    # SPA: all routes fall back to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets aggressively
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;
    gzip_comp_level 6;
}
```

## Common Config Examples

### Full Production Config
```
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;              # 1 worker per CPU core
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;         # max connections per worker
    multi_accept on;
    use epoll;                       # Linux optimal event method
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time $upstream_response_time';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;
    gzip_comp_level 6;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;

    # Include site configs
    include /etc/nginx/conf.d/*.conf;
}
```

### Reverse Proxy + Static Files + SSL
```
upstream app_backend {
    least_conn;
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
}

server {
    listen 443 ssl http2;
    server_name mysite.com;

    ssl_certificate     /etc/letsencrypt/live/mysite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mysite.com/privkey.pem;

    # Static files served by Nginx directly
    location /static/ {
        alias /var/www/mysite/static/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/mysite/media/;
        expires 7d;
    }

    # API routes to application
    location /api/ {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SPA frontend
    location / {
        root /var/www/mysite/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name mysite.com;
    return 301 https://$host$request_uri;
}
```

### WebSocket Proxy
```
# WebSocket proxying
server {
    listen 80;
    server_name ws.mysite.com;

    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Longer timeouts for WebSocket connections
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

## Useful Commands
```
commands:
  test_config: "nginx -t"
  reload_config: "nginx -s reload"
  stop: "nginx -s stop"
  start: "systemctl start nginx"
  view_logs: "tail -f /var/log/nginx/access.log"
  view_errors: "tail -f /var/log/nginx/error.log"
  check_version: "nginx -v"
  show_compiled_modules: "nginx -V"
```

## Tags
```
tags:
  - nginx
  - reverse-proxy
  - load-balancing
  - web-server
  - ssl-termination
  - rate-limiting
  - proxy-pass
  - upstream
  - static-files
  - devops
```
