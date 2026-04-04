# HTTP & HTTPS

## What is HTTP
```
overview:
  full_name: HyperText Transfer Protocol
  type: Application-layer protocol for transmitting hypermedia documents
  transport: TCP (HTTP/1.1, HTTP/2), UDP via QUIC (HTTP/3)
  default_ports:
    http: 80
    https: 443
  standard: RFC 7230-7235 (HTTP/1.1), RFC 7540 (HTTP/2), RFC 9114 (HTTP/3)
  model: Request-Response (client sends request, server sends response)

key_features:
  - Stateless protocol (each request is independent)
  - Text-based in HTTP/1.1, binary framing in HTTP/2+
  - Extensible via headers
  - Supports caching, authentication, content negotiation
  - Foundation of data communication on the Web
```

## Request-Response Cycle
```
http_cycle:
  1_client_connects:
    description: Client opens TCP connection to server (+ TLS handshake for HTTPS)
    note: HTTP/1.1 uses keep-alive to reuse connections

  2_client_sends_request:
    format: |
      GET /api/users/1 HTTP/1.1
      Host: example.com
      Accept: application/json
      Authorization: Bearer <token>
    parts:
      request_line: "METHOD /path HTTP/version"
      headers: "Key-value metadata (Host, Accept, Content-Type, etc.)"
      body: "Optional payload (for POST, PUT, PATCH)"

  3_server_processes:
    description: Server routes request, executes handler, builds response

  4_server_sends_response:
    format: |
      HTTP/1.1 200 OK
      Content-Type: application/json
      Content-Length: 52

      {"id": 1, "name": "Ankit", "role": "engineer"}
    parts:
      status_line: "HTTP/version STATUS_CODE REASON"
      headers: "Response metadata (Content-Type, Set-Cookie, Cache-Control)"
      body: "Response payload"
```

## HTTP Methods
```
methods:
  GET:
    purpose: Retrieve a resource
    body: No
    idempotent: Yes
    safe: Yes
    cacheable: Yes
    example: "GET /api/users/1"

  POST:
    purpose: Create a new resource or trigger an action
    body: Yes
    idempotent: No
    safe: No
    cacheable: No (unless explicit headers)
    example: "POST /api/users with JSON body"

  PUT:
    purpose: Replace an entire resource
    body: Yes
    idempotent: Yes
    safe: No
    cacheable: No
    example: "PUT /api/users/1 with full user JSON"

  PATCH:
    purpose: Partially update a resource
    body: Yes
    idempotent: No (can be, but not guaranteed)
    safe: No
    cacheable: No
    example: "PATCH /api/users/1 with partial JSON"

  DELETE:
    purpose: Remove a resource
    body: Optional
    idempotent: Yes
    safe: No
    cacheable: No
    example: "DELETE /api/users/1"

  HEAD:
    purpose: Same as GET but returns only headers (no body)
    use_case: Check if resource exists, get content length
    idempotent: Yes
    safe: Yes

  OPTIONS:
    purpose: Describe communication options for a resource
    use_case: CORS preflight requests
    idempotent: Yes
    safe: Yes

key_terms:
  safe: Does not modify server state
  idempotent: Multiple identical requests have same effect as one
```

## Status Codes
```
status_codes:
  1xx_informational:
    100: Continue - Server received headers, client should send body
    101: Switching Protocols - Server switching to WebSocket or HTTP/2

  2xx_success:
    200: OK - Request succeeded
    201: Created - Resource created (POST response)
    204: No Content - Success but no body (DELETE response)

  3xx_redirection:
    301: Moved Permanently - Resource has new permanent URL
    302: Found - Temporary redirect (keep original method debated)
    304: Not Modified - Cached version is still valid
    307: Temporary Redirect - Same method, temporary new URL
    308: Permanent Redirect - Same method, permanent new URL

  4xx_client_error:
    400: Bad Request - Malformed request syntax
    401: Unauthorized - Authentication required
    403: Forbidden - Authenticated but not authorized
    404: Not Found - Resource does not exist
    405: Method Not Allowed - HTTP method not supported for this resource
    408: Request Timeout - Server timed out waiting for request
    409: Conflict - Request conflicts with current state (duplicate, version mismatch)
    413: Payload Too Large - Request body exceeds server limit
    422: Unprocessable Entity - Validation error (WebDAV, widely adopted)
    429: Too Many Requests - Rate limit exceeded

  5xx_server_error:
    500: Internal Server Error - Generic server failure
    502: Bad Gateway - Upstream server sent invalid response
    503: Service Unavailable - Server overloaded or in maintenance
    504: Gateway Timeout - Upstream server did not respond in time
```

## Common Headers
```
headers:
  request_headers:
    Host: "Target server hostname (required in HTTP/1.1)"
    Accept: "Media types client can handle (application/json, text/html)"
    Content-Type: "Media type of request body (application/json, multipart/form-data)"
    Authorization: "Credentials (Bearer <token>, Basic base64)"
    User-Agent: "Client software identifier"
    Accept-Encoding: "Compression algorithms supported (gzip, br, deflate)"
    Accept-Language: "Preferred languages (en-US, fr)"
    Cookie: "Previously set cookies sent back to server"
    If-None-Match: "ETag from previous response (for conditional requests)"
    If-Modified-Since: "Date from previous response (for conditional requests)"

  response_headers:
    Content-Type: "Media type of response body"
    Content-Length: "Size of response body in bytes"
    Set-Cookie: "Instruct browser to store a cookie"
    Cache-Control: "Caching directives (max-age, no-cache, no-store)"
    ETag: "Unique identifier for resource version"
    Last-Modified: "When resource was last changed"
    Location: "URL to redirect to (used with 3xx status)"
    Access-Control-Allow-Origin: "CORS header (which origins can access)"
    X-RateLimit-Remaining: "API rate limit remaining calls"

  content_negotiation:
    description: Server selects best representation based on client headers
    flow:
      - Client sends Accept, Accept-Language, Accept-Encoding
      - Server picks best match from available representations
      - Server responds with Content-Type, Content-Language, Content-Encoding
    example:
      request: "Accept: application/json, text/html;q=0.9"
      meaning: "Prefers JSON, but accepts HTML with lower priority"
      q_values: "Quality factor 0-1, default is 1, higher = more preferred"
```

## Cookies
```
cookies:
  what: Small pieces of data server sends to browser, browser stores and sends back
  purpose:
    - Session management (login, shopping cart)
    - Personalization (user preferences)
    - Tracking (analytics)

  set_cookie_header:
    format: "Set-Cookie: name=value; attributes"
    example: "Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=3600"

  attributes:
    Domain: "Which domain the cookie is sent to"
    Path: "URL path scope for the cookie"
    Expires: "Absolute expiry date"
    Max-Age: "Seconds until cookie expires (overrides Expires)"
    Secure: "Only send over HTTPS"
    HttpOnly: "Not accessible via JavaScript (prevents XSS theft)"
    SameSite:
      Strict: "Only sent for same-site requests"
      Lax: "Sent for same-site + top-level navigations (default in modern browsers)"
      None: "Sent for all requests (requires Secure)"
```

## Caching
```
caching:
  cache_control_directives:
    no-store: "Do not cache at all (sensitive data)"
    no-cache: "Cache but revalidate with server before using"
    max-age: "Cache is valid for N seconds (max-age=3600 = 1 hour)"
    s-maxage: "Same as max-age but for shared caches (CDN)"
    public: "Any cache can store (CDN, proxy)"
    private: "Only browser cache, not CDN"
    must-revalidate: "After expiry, must check with server"
    immutable: "Resource will never change (use for versioned assets)"

  validation_mechanisms:
    etag:
      description: Unique hash of resource content
      flow:
        - Server sends ETag in response header
        - Client sends If-None-Match with stored ETag
        - If match, server returns 304 Not Modified (no body)
        - If no match, server returns 200 with new content
    last_modified:
      description: Timestamp of last modification
      flow:
        - Server sends Last-Modified header
        - Client sends If-Modified-Since header
        - If not modified, server returns 304

  cache_locations:
    browser_cache: "Private, per-user"
    proxy_cache: "Shared, intermediate server"
    cdn_cache: "Edge servers distributed globally"
    reverse_proxy: "Nginx, Varnish in front of app server"

  best_practices:
    - "Versioned static assets: Cache-Control: public, max-age=31536000, immutable"
    - "API responses: Cache-Control: no-cache with ETag for validation"
    - "User-specific data: Cache-Control: private, max-age=0, must-revalidate"
    - "Sensitive data: Cache-Control: no-store"
```

## HTTPS & TLS
```
https:
  what: HTTP over TLS (Transport Layer Security)
  purpose:
    - Encryption (data cannot be read in transit)
    - Authentication (server proves identity via certificate)
    - Integrity (data cannot be tampered with)

  tls_handshake:
    description: Establishes secure connection before any HTTP data
    tls_1_3_flow:
      1_client_hello:
        sends:
          - Supported TLS versions
          - Supported cipher suites
          - Client random number
          - Key share (Diffie-Hellman public key)
      2_server_hello:
        sends:
          - Chosen cipher suite
          - Server random number
          - Server key share
          - Server certificate
          - Certificate verify (signature)
          - Finished message
      3_client_finished:
        does:
          - Verifies server certificate against trusted CAs
          - Computes shared secret from key exchange
          - Sends Finished message
      4_secure_channel:
        result: All subsequent data encrypted with shared symmetric key

    tls_1_3_improvements:
      - 1-RTT handshake (vs 2-RTT in TLS 1.2)
      - 0-RTT resumption for repeat connections
      - Removed insecure algorithms (RC4, SHA-1, RSA key exchange)
      - Forward secrecy mandatory (ephemeral Diffie-Hellman)

  certificates:
    what: Digital certificate proving server identity
    issuer: Certificate Authority (CA) like Let's Encrypt, DigiCert
    contains:
      - Domain name
      - Public key
      - Issuer info
      - Validity period
      - Digital signature from CA
    chain_of_trust: "Browser trusts Root CA -> Root CA signs Intermediate CA -> Intermediate signs server cert"
```

## HTTP/1.1 vs HTTP/2 vs HTTP/3
```
version_comparison:
  http_1_1:
    year: 1997
    transport: TCP
    format: Text-based
    multiplexing: No (one request per connection at a time)
    workaround: Open 6 parallel TCP connections per domain
    head_of_line_blocking: Yes (at TCP and HTTP level)
    header_compression: No
    server_push: No
    connection: Keep-alive (reuse TCP connection)

  http_2:
    year: 2015
    transport: TCP
    format: Binary framing layer
    multiplexing: Yes (multiple streams over single TCP connection)
    head_of_line_blocking: Solved at HTTP level, still exists at TCP level
    header_compression: HPACK (reduces redundant headers)
    server_push: Yes (server can send resources before client requests)
    stream_prioritization: Yes (weight and dependency)
    key_improvement: One TCP connection handles all requests in parallel

  http_3:
    year: 2022
    transport: QUIC (UDP-based)
    format: Binary
    multiplexing: Yes (over QUIC streams)
    head_of_line_blocking: Fully solved (packet loss affects only one stream)
    header_compression: QPACK
    server_push: Yes
    connection_migration: Yes (switch networks without reconnecting)
    0_rtt: Yes (faster connection establishment for repeat visits)
    key_improvement: Eliminates TCP head-of-line blocking, faster handshakes

  head_of_line_blocking_explained:
    http_1_1: "Request 2 waits for Request 1 to complete on same connection"
    http_2: "HTTP streams are independent, but TCP treats all bytes as one stream - one lost packet blocks all streams"
    http_3: "QUIC handles each stream independently - lost packet in stream A does not block stream B"
```

## Code Examples

### Simple HTTP Server in Go
```go
package main

import (
	"encoding/json"
	"log"
	"net/http"
)

type User struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/users/{id}", func(w http.ResponseWriter, r *http.Request) {
		id := r.PathValue("id")
		user := User{ID: 1, Name: "Ankit", Email: "ankit@example.com"}

		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Cache-Control", "private, max-age=60")
		w.Header().Set("ETag", `"user-1-v3"`)

		// Check conditional request
		if r.Header.Get("If-None-Match") == `"user-1-v3"` {
			w.WriteHeader(http.StatusNotModified)
			return
		}

		_ = id
		json.NewEncoder(w).Encode(user)
	})

	mux.HandleFunc("POST /api/users", func(w http.ResponseWriter, r *http.Request) {
		var user User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			http.Error(w, `{"error":"invalid JSON"}`, http.StatusBadRequest)
			return
		}
		user.ID = 42
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Location", "/api/users/42")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(user)
	})

	log.Println("Server running on :8080")
	log.Fatal(http.ListenAndServe(":8080", mux))
}
```

### HTTP Client in Go
```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

func main() {
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// GET request with headers
	req, _ := http.NewRequest("GET", "https://api.example.com/users/1", nil)
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Authorization", "Bearer my-token")

	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	fmt.Printf("Status: %d\n", resp.StatusCode)
	fmt.Printf("Content-Type: %s\n", resp.Header.Get("Content-Type"))

	body, _ := io.ReadAll(resp.Body)
	fmt.Println(string(body))

	// POST request with JSON body
	payload := map[string]string{"name": "Ankit", "email": "ankit@example.com"}
	jsonBody, _ := json.Marshal(payload)

	resp2, err := http.Post(
		"https://api.example.com/users",
		"application/json",
		bytes.NewBuffer(jsonBody),
	)
	if err != nil {
		panic(err)
	}
	defer resp2.Body.Close()
	fmt.Printf("Created: %d\n", resp2.StatusCode)
}
```

### Fetch API in JavaScript
```javascript
// GET request
const response = await fetch("https://api.example.com/users/1", {
  method: "GET",
  headers: {
    Accept: "application/json",
    Authorization: "Bearer my-token",
  },
});

if (response.status === 304) {
  console.log("Not modified, use cached version");
}

const user = await response.json();
console.log(user);

// POST request
const createResponse = await fetch("https://api.example.com/users", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ name: "Ankit", email: "ankit@example.com" }),
});

if (createResponse.status === 201) {
  const newUser = await createResponse.json();
  console.log("Created:", newUser);
  console.log("Location:", createResponse.headers.get("Location"));
}

// Using AbortController for timeout
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000);

try {
  const res = await fetch("https://api.example.com/slow", {
    signal: controller.signal,
  });
} catch (err) {
  if (err.name === "AbortError") {
    console.log("Request timed out");
  }
}
```

### HTTPS Server in Go
```go
package main

import (
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// HSTS header - tell browser to always use HTTPS
		w.Header().Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
		w.Write([]byte("Hello, HTTPS!"))
	})

	// Redirect HTTP to HTTPS
	go func() {
		redirect := http.NewServeMux()
		redirect.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			target := "https://" + r.Host + r.URL.RequestURI()
			http.Redirect(w, r, target, http.StatusMovedPermanently)
		})
		log.Fatal(http.ListenAndServe(":80", redirect))
	}()

	// TLS server (cert.pem and key.pem from Let's Encrypt or self-signed)
	log.Println("HTTPS server on :443")
	log.Fatal(http.ListenAndServeTLS(":443", "cert.pem", "key.pem", mux))
}
```
