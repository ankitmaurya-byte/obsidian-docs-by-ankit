# CORS

## What is CORS
```
overview:
  full_name: Cross-Origin Resource Sharing
  type: HTTP-header based security mechanism
  purpose: Allows servers to declare which origins can access their resources
  enforced_by: Browser (not the server)
  specification: W3C / Fetch Standard

  key_concept: |
    By default, browsers block web pages from making requests to a different
    origin (domain, protocol, or port). CORS relaxes this restriction by
    letting servers explicitly allow cross-origin access.

same_origin_policy:
  definition: Browser security policy that restricts scripts from one origin accessing resources from another
  origin_is: "protocol + domain + port"
  examples:
    same_origin:
      - "https://example.com/page1 -> https://example.com/page2  (same)"
      - "https://example.com/api -> https://example.com/data    (same)"
    different_origin:
      - "https://example.com -> http://example.com       (different protocol)"
      - "https://example.com -> https://api.example.com  (different subdomain)"
      - "https://example.com -> https://example.com:8080 (different port)"
      - "https://example.com -> https://other.com        (different domain)"
```

## How CORS Works
```
flow:
  1_browser_detects_cross_origin:
    description: JavaScript on origin A tries to fetch from origin B
    example: "Frontend on localhost:3000 calls API on localhost:8080"

  2_browser_adds_origin_header:
    description: Browser automatically adds Origin header to the request
    header: "Origin: http://localhost:3000"

  3_server_responds_with_cors_headers:
    description: Server checks Origin and responds with Access-Control headers
    key_header: "Access-Control-Allow-Origin: http://localhost:3000"

  4_browser_checks_headers:
    allow: If response headers permit the origin, browser delivers the response
    block: If headers are missing or wrong, browser blocks the response
    note: Server STILL processes the request, browser just hides the response

cors_headers:
  response_headers:
    Access-Control-Allow-Origin:
      description: Which origins are allowed
      values:
        - "* (any origin, cannot use with credentials)"
        - "https://example.com (specific origin)"
      note: Can only be one value or *, not a list

    Access-Control-Allow-Methods:
      description: Which HTTP methods are allowed
      example: "GET, POST, PUT, DELETE, OPTIONS"

    Access-Control-Allow-Headers:
      description: Which custom headers the client can send
      example: "Content-Type, Authorization, X-Request-ID"

    Access-Control-Expose-Headers:
      description: Which response headers JavaScript can read
      example: "X-Total-Count, X-Request-ID"
      note: By default, only simple headers are exposed to JS

    Access-Control-Allow-Credentials:
      description: Whether cookies/auth headers are allowed
      value: "true"
      restriction: Cannot use with Allow-Origin=*

    Access-Control-Max-Age:
      description: How long preflight result can be cached (seconds)
      example: "86400 (24 hours)"
```

## Simple vs Preflighted Requests
```
simple_requests:
  definition: Requests that do NOT trigger a preflight check
  conditions_all_must_be_true:
    method: "GET, HEAD, or POST"
    headers: "Only simple headers (Accept, Accept-Language, Content-Language, Content-Type)"
    content_type: "Only application/x-www-form-urlencoded, multipart/form-data, or text/plain"

  flow:
    1: "Browser sends the actual request with Origin header"
    2: "Server responds with Access-Control-Allow-Origin"
    3: "Browser checks header and allows/blocks response"

preflighted_requests:
  definition: Browser sends an OPTIONS request BEFORE the actual request
  triggered_when:
    - "Method is PUT, DELETE, PATCH, or others"
    - "Custom headers like Authorization, X-Custom-Header"
    - "Content-Type is application/json"
    - "Basically anything beyond a simple form submission"

  flow:
    1_preflight:
      method: OPTIONS
      headers:
        Origin: "http://localhost:3000"
        Access-Control-Request-Method: "PUT"
        Access-Control-Request-Headers: "Content-Type, Authorization"

    2_preflight_response:
      status: "204 No Content"
      headers:
        Access-Control-Allow-Origin: "http://localhost:3000"
        Access-Control-Allow-Methods: "GET, POST, PUT, DELETE"
        Access-Control-Allow-Headers: "Content-Type, Authorization"
        Access-Control-Max-Age: "86400"

    3_actual_request:
      description: Browser sends the real request only if preflight succeeded

  note: Preflight is entirely browser-driven, your JS code never sees it
```

## Credentials (Cookies, Auth Headers)
```
credentials:
  problem: |
    By default, cross-origin requests do NOT include cookies or
    Authorization headers. You must opt-in on both client and server.

  client_side:
    fetch: 'fetch(url, { credentials: "include" })'
    axios: "axios.defaults.withCredentials = true"
    xhr: "xhr.withCredentials = true"

  server_side:
    required_headers:
      Access-Control-Allow-Credentials: "true"
      Access-Control-Allow-Origin: "Must be a specific origin (NOT *)"

  important: |
    When credentials are involved:
    - Access-Control-Allow-Origin CANNOT be *
    - Access-Control-Allow-Headers CANNOT be *
    - Access-Control-Allow-Methods CANNOT be *
    You must specify exact values for each.
```

## Common CORS Errors and Fixes
```
common_errors:
  no_allow_origin:
    error: "Access to fetch has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header"
    cause: Server does not send CORS headers
    fix: Add Access-Control-Allow-Origin header on the server

  wildcard_with_credentials:
    error: "Cannot use wildcard in Access-Control-Allow-Origin when credentials flag is true"
    cause: "Server sends Allow-Origin=* but client sends credentials"
    fix: Set Allow-Origin to the specific requesting origin

  preflight_fails:
    error: "Response to preflight request doesn't pass access control check"
    cause: Server doesn't handle OPTIONS method or returns wrong headers
    fix: Add OPTIONS handler that returns correct CORS preflight headers

  missing_allowed_header:
    error: "Request header field authorization is not allowed by Access-Control-Allow-Headers"
    cause: Server does not list the header in Allow-Headers
    fix: "Add the header to Access-Control-Allow-Headers"

  method_not_allowed:
    error: "Method PUT is not allowed by Access-Control-Allow-Methods"
    cause: Preflight response doesn't include the method
    fix: "Add the method to Access-Control-Allow-Methods"

debugging_tips:
  - Check browser DevTools Network tab for the OPTIONS preflight request
  - Look at the response headers on the preflight response
  - Make sure your server handles OPTIONS requests (some frameworks strip them)
  - CORS is browser-only, curl and Postman do not enforce it
  - If using a reverse proxy (Nginx), CORS headers might get duplicated or stripped
```

## Code Examples

### CORS Middleware in Go (net/http)
```go
package main

import (
    "encoding/json"
    "net/http"
)

func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        origin := r.Header.Get("Origin")

        // Allow specific origins (check against a whitelist in production)
        allowedOrigins := map[string]bool{
            "http://localhost:3000": true,
            "https://myapp.com":    true,
        }

        if allowedOrigins[origin] {
            w.Header().Set("Access-Control-Allow-Origin", origin)
            w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
            w.Header().Set("Access-Control-Allow-Credentials", "true")
            w.Header().Set("Access-Control-Max-Age", "86400")
        }

        // Handle preflight
        if r.Method == http.MethodOptions {
            w.WriteHeader(http.StatusNoContent)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func main() {
    mux := http.NewServeMux()

    mux.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{"message": "Hello from API"})
    })

    // Wrap all routes with CORS middleware
    http.ListenAndServe(":8080", corsMiddleware(mux))
}
```

### CORS with rs/cors Package (Go)
```go
package main

import (
    "net/http"
    "github.com/rs/cors"
)

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte(`{"status":"ok"}`))
    })

    c := cors.New(cors.Options{
        AllowedOrigins:   []string{"http://localhost:3000", "https://myapp.com"},
        AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE"},
        AllowedHeaders:   []string{"Content-Type", "Authorization"},
        AllowCredentials: true,
        MaxAge:           86400,
    })

    http.ListenAndServe(":8080", c.Handler(mux))
}
```

### CORS in Node.js (Express)
```javascript
const express = require('express');
const cors = require('cors');
const app = express();

// Option 1: Allow all origins (development only)
app.use(cors());

// Option 2: Configure specific origins
app.use(cors({
    origin: ['http://localhost:3000', 'https://myapp.com'],
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
    maxAge: 86400,
}));

// Option 3: Dynamic origin check
app.use(cors({
    origin: (origin, callback) => {
        const allowedOrigins = ['http://localhost:3000', 'https://myapp.com'];
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
    credentials: true,
}));

app.get('/api/data', (req, res) => {
    res.json({ message: 'Hello from API' });
});

app.listen(8080, () => console.log('Server on :8080'));
```

### CORS Manual Middleware in Node.js (No Library)
```javascript
const express = require('express');
const app = express();

app.use((req, res, next) => {
    const allowedOrigins = ['http://localhost:3000', 'https://myapp.com'];
    const origin = req.headers.origin;

    if (allowedOrigins.includes(origin)) {
        res.setHeader('Access-Control-Allow-Origin', origin);
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        res.setHeader('Access-Control-Allow-Credentials', 'true');
        res.setHeader('Access-Control-Max-Age', '86400');
    }

    if (req.method === 'OPTIONS') {
        return res.sendStatus(204);
    }

    next();
});

app.get('/api/data', (req, res) => {
    res.json({ message: 'Hello from API' });
});

app.listen(8080);
```

### Frontend Fetch with CORS
```javascript
// Simple request (no preflight)
fetch('http://localhost:8080/api/data')
    .then(res => res.json())
    .then(data => console.log(data));

// Request with credentials (cookies)
fetch('http://localhost:8080/api/data', {
    credentials: 'include',
})
    .then(res => res.json())
    .then(data => console.log(data));

// Request that triggers preflight (custom headers + JSON)
fetch('http://localhost:8080/api/data', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9...',
    },
    credentials: 'include',
    body: JSON.stringify({ name: 'ankit' }),
})
    .then(res => res.json())
    .then(data => console.log(data));
```

## Tags
```
tags:
  - cors
  - cross-origin
  - same-origin-policy
  - preflight
  - http-headers
  - security
  - browser
  - web
```
