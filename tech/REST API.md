# REST API

## What is REST
```
overview:
  full_name: Representational State Transfer
  type: Architectural style for designing networked applications
  created_by: Roy Fielding (2000, PhD dissertation)
  transport: HTTP
  format: Typically JSON (also XML, YAML, Protobuf)
  note: REST is not a protocol, it is a set of constraints

key_features:
  - Stateless communication
  - Resource-based (nouns, not verbs)
  - Standard HTTP methods for operations
  - Uniform interface
  - Cacheable responses
  - Layered system architecture
```

## REST Principles
```
constraints:
  client_server:
    description: Client and server are separate, independent systems
    benefit: Client and server can evolve independently

  stateless:
    description: Each request contains all information needed to process it
    benefit: Server does not store client session state between requests
    implication: Authentication token must be sent with every request

  cacheable:
    description: Responses must indicate if they can be cached
    benefit: Reduces server load, improves client performance
    how: Use Cache-Control, ETag, Last-Modified headers

  uniform_interface:
    description: Consistent way to interact with resources
    sub_constraints:
      resource_identification: "Resources identified by URIs (/api/users/1)"
      resource_manipulation: "Use representations (JSON) to modify resources"
      self_descriptive_messages: "Response includes Content-Type, status code"
      hateoas: "Response includes links to related actions"

  layered_system:
    description: Client cannot tell if connected directly to server or intermediary
    benefit: Load balancers, caches, gateways can be inserted transparently

  code_on_demand:
    description: Server can send executable code to client (optional)
    example: JavaScript sent from server to run in browser
```

## Resource Naming Conventions
```
naming:
  rules:
    - Use nouns, not verbs (resources, not actions)
    - Use plural nouns for collections
    - Use lowercase with hyphens for multi-word
    - Use path hierarchy for relationships
    - Keep URLs short and readable

  good_examples:
    collection: "GET /api/users"
    single_resource: "GET /api/users/42"
    nested_resource: "GET /api/users/42/orders"
    specific_nested: "GET /api/users/42/orders/7"
    filtering: "GET /api/users?role=admin&status=active"
    searching: "GET /api/users?q=ankit"
    multi_word: "GET /api/blog-posts"

  bad_examples:
    - "GET /api/getUsers (verb in URL)"
    - "GET /api/user (singular for collection)"
    - "POST /api/users/create (verb + redundant with POST)"
    - "GET /api/users/42/getOrders (verb in URL)"
    - "DELETE /api/deleteUser/42 (verb in URL)"
```

## HTTP Methods to CRUD Mapping
```
crud_mapping:
  create:
    method: POST
    url: "/api/users"
    body: '{"name": "Ankit", "email": "ankit@example.com"}'
    success_status: 201 Created
    response_headers: "Location: /api/users/42"
    response_body: "Created resource with server-generated ID"

  read_collection:
    method: GET
    url: "/api/users"
    body: None
    success_status: 200 OK
    response_body: "Array of resources"

  read_single:
    method: GET
    url: "/api/users/42"
    body: None
    success_status: 200 OK
    response_body: "Single resource object"

  update_full:
    method: PUT
    url: "/api/users/42"
    body: '{"name": "Ankit", "email": "new@example.com"}'
    success_status: 200 OK
    note: Replaces entire resource, all fields required

  update_partial:
    method: PATCH
    url: "/api/users/42"
    body: '{"email": "new@example.com"}'
    success_status: 200 OK
    note: Updates only specified fields

  delete:
    method: DELETE
    url: "/api/users/42"
    body: None
    success_status: 204 No Content
```

## Status Codes for APIs
```
api_status_codes:
  success:
    200: "OK - GET, PUT, PATCH succeeded"
    201: "Created - POST created a new resource"
    204: "No Content - DELETE succeeded, or update with no response body"

  client_errors:
    400: "Bad Request - Invalid JSON, missing required fields"
    401: "Unauthorized - No token or invalid token"
    403: "Forbidden - Valid token but insufficient permissions"
    404: "Not Found - Resource does not exist"
    405: "Method Not Allowed - e.g., POST on a read-only resource"
    409: "Conflict - Duplicate entry, version conflict"
    422: "Unprocessable Entity - Validation failed (valid JSON but bad data)"
    429: "Too Many Requests - Rate limited"

  server_errors:
    500: "Internal Server Error - Bug in server code"
    502: "Bad Gateway - Upstream service down"
    503: "Service Unavailable - Server overloaded or maintenance"

  error_response_format:
    example: |
      {
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "Email is required",
          "details": [
            {"field": "email", "message": "must not be empty"}
          ]
        }
      }
```

## API Versioning
```
versioning:
  strategies:
    url_path:
      format: "/api/v1/users"
      pros: Clear, easy to understand, easy to route
      cons: URL changes between versions
      usage: Most common approach

    query_parameter:
      format: "/api/users?version=1"
      pros: URL stays the same
      cons: Easy to forget, less visible

    header:
      format: "Accept: application/vnd.myapi.v1+json"
      pros: Clean URLs, proper content negotiation
      cons: Harder to test in browser, less discoverable

    custom_header:
      format: "X-API-Version: 1"
      pros: Simple to implement
      cons: Non-standard

  best_practice:
    recommendation: URL path versioning (/api/v1/)
    reasons:
      - Most widely adopted
      - Easy to route at load balancer/gateway level
      - Simple for API consumers to understand
      - Easy to deprecate old versions
```

## Pagination
```
pagination:
  offset_based:
    description: Skip N items, take M items
    request: "GET /api/users?offset=20&limit=10"
    response: |
      {
        "data": [...],
        "pagination": {
          "offset": 20,
          "limit": 10,
          "total": 150
        }
      }
    pros: Simple, allows jumping to any page
    cons: Inconsistent results if data changes, slow for large offsets (DB scans)

  cursor_based:
    description: Use opaque cursor to fetch next page
    request: "GET /api/users?cursor=eyJpZCI6NDJ9&limit=10"
    response: |
      {
        "data": [...],
        "pagination": {
          "next_cursor": "eyJpZCI6NTJ9",
          "has_more": true
        }
      }
    pros: Consistent results, efficient for DB (WHERE id > cursor)
    cons: Cannot jump to arbitrary page

  page_based:
    description: Page number with page size
    request: "GET /api/users?page=3&per_page=10"
    response: |
      {
        "data": [...],
        "pagination": {
          "page": 3,
          "per_page": 10,
          "total_pages": 15,
          "total": 150
        }
      }

  best_practice: "Cursor-based for large/real-time datasets, offset for small/static datasets"
```

## Filtering and Sorting
```
filtering:
  query_parameters:
    equality: "GET /api/users?role=admin&status=active"
    comparison: "GET /api/products?price_min=10&price_max=100"
    search: "GET /api/users?q=ankit"
    date_range: "GET /api/orders?created_after=2025-01-01&created_before=2025-12-31"

  sorting:
    single_field: "GET /api/users?sort=created_at"
    descending: "GET /api/users?sort=-created_at"
    multiple: "GET /api/users?sort=-created_at,name"

  field_selection:
    description: Return only specified fields (reduces payload)
    request: "GET /api/users?fields=id,name,email"
```

## HATEOAS
```
hateoas:
  full_name: Hypermedia As The Engine Of Application State
  description: API responses include links to related actions and resources
  benefit: Client discovers available actions dynamically, does not hardcode URLs

  example:
    request: "GET /api/users/42"
    response: |
      {
        "id": 42,
        "name": "Ankit",
        "email": "ankit@example.com",
        "links": [
          {"rel": "self", "href": "/api/users/42", "method": "GET"},
          {"rel": "update", "href": "/api/users/42", "method": "PUT"},
          {"rel": "delete", "href": "/api/users/42", "method": "DELETE"},
          {"rel": "orders", "href": "/api/users/42/orders", "method": "GET"}
        ]
      }

  reality: Most REST APIs do not implement full HATEOAS
```

## Best Practices
```
best_practices:
  design:
    - Use consistent naming conventions across all endpoints
    - Version your API from day one
    - Use proper HTTP status codes (not 200 for everything)
    - Return created resource on POST (with Location header)
    - Support filtering, sorting, pagination on list endpoints
    - Use JSON as default format

  security:
    - Always use HTTPS
    - Use Bearer tokens (JWT or opaque) for auth
    - Implement rate limiting (429 responses)
    - Validate all input server-side
    - Do not expose internal IDs if sequential (use UUIDs)
    - Add CORS headers for browser clients

  performance:
    - Enable gzip/brotli compression
    - Set appropriate Cache-Control headers
    - Support conditional requests (ETag, If-None-Match)
    - Use field selection to reduce payload size
    - Implement pagination (never return unbounded lists)

  error_handling:
    - Use consistent error response format
    - Include machine-readable error codes
    - Include human-readable messages
    - Return validation errors per field
    - Do not leak stack traces in production
```

## Code Examples

### REST API Server in Go
```go
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"sync"
)

type User struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

type ErrorResponse struct {
	Error struct {
		Code    string `json:"code"`
		Message string `json:"message"`
	} `json:"error"`
}

type ListResponse struct {
	Data       []User     `json:"data"`
	Pagination Pagination `json:"pagination"`
}

type Pagination struct {
	Page      int `json:"page"`
	PerPage   int `json:"per_page"`
	Total     int `json:"total"`
	TotalPages int `json:"total_pages"`
}

var (
	users  = map[int]User{}
	nextID = 1
	mu     sync.RWMutex
)

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func writeError(w http.ResponseWriter, status int, code, message string) {
	resp := ErrorResponse{}
	resp.Error.Code = code
	resp.Error.Message = message
	writeJSON(w, status, resp)
}

func main() {
	mux := http.NewServeMux()

	// GET /api/v1/users - List users with pagination
	mux.HandleFunc("GET /api/v1/users", func(w http.ResponseWriter, r *http.Request) {
		page, _ := strconv.Atoi(r.URL.Query().Get("page"))
		if page < 1 {
			page = 1
		}
		perPage, _ := strconv.Atoi(r.URL.Query().Get("per_page"))
		if perPage < 1 || perPage > 100 {
			perPage = 20
		}

		mu.RLock()
		all := make([]User, 0, len(users))
		for _, u := range users {
			all = append(all, u)
		}
		mu.RUnlock()

		total := len(all)
		start := (page - 1) * perPage
		end := start + perPage
		if start > total {
			start = total
		}
		if end > total {
			end = total
		}

		writeJSON(w, http.StatusOK, ListResponse{
			Data: all[start:end],
			Pagination: Pagination{
				Page:       page,
				PerPage:    perPage,
				Total:      total,
				TotalPages: (total + perPage - 1) / perPage,
			},
		})
	})

	// GET /api/v1/users/{id} - Get single user
	mux.HandleFunc("GET /api/v1/users/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, err := strconv.Atoi(r.PathValue("id"))
		if err != nil {
			writeError(w, http.StatusBadRequest, "INVALID_ID", "ID must be an integer")
			return
		}

		mu.RLock()
		user, ok := users[id]
		mu.RUnlock()

		if !ok {
			writeError(w, http.StatusNotFound, "NOT_FOUND", "User not found")
			return
		}
		writeJSON(w, http.StatusOK, user)
	})

	// POST /api/v1/users - Create user
	mux.HandleFunc("POST /api/v1/users", func(w http.ResponseWriter, r *http.Request) {
		var user User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			writeError(w, http.StatusBadRequest, "INVALID_JSON", "Request body must be valid JSON")
			return
		}
		if user.Name == "" || user.Email == "" {
			writeError(w, http.StatusUnprocessableEntity, "VALIDATION_ERROR", "Name and email are required")
			return
		}

		mu.Lock()
		user.ID = nextID
		nextID++
		users[user.ID] = user
		mu.Unlock()

		w.Header().Set("Location", "/api/v1/users/"+strconv.Itoa(user.ID))
		writeJSON(w, http.StatusCreated, user)
	})

	// PUT /api/v1/users/{id} - Replace user
	mux.HandleFunc("PUT /api/v1/users/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, err := strconv.Atoi(r.PathValue("id"))
		if err != nil {
			writeError(w, http.StatusBadRequest, "INVALID_ID", "ID must be an integer")
			return
		}

		var user User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			writeError(w, http.StatusBadRequest, "INVALID_JSON", "Request body must be valid JSON")
			return
		}

		mu.Lock()
		if _, ok := users[id]; !ok {
			mu.Unlock()
			writeError(w, http.StatusNotFound, "NOT_FOUND", "User not found")
			return
		}
		user.ID = id
		users[id] = user
		mu.Unlock()

		writeJSON(w, http.StatusOK, user)
	})

	// DELETE /api/v1/users/{id} - Delete user
	mux.HandleFunc("DELETE /api/v1/users/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, err := strconv.Atoi(r.PathValue("id"))
		if err != nil {
			writeError(w, http.StatusBadRequest, "INVALID_ID", "ID must be an integer")
			return
		}

		mu.Lock()
		if _, ok := users[id]; !ok {
			mu.Unlock()
			writeError(w, http.StatusNotFound, "NOT_FOUND", "User not found")
			return
		}
		delete(users, id)
		mu.Unlock()

		w.WriteHeader(http.StatusNoContent)
	})

	log.Println("REST API server on :8080")
	log.Fatal(http.ListenAndServe(":8080", mux))
}
```

### REST API Client in JavaScript
```javascript
const BASE_URL = "http://localhost:8080/api/v1";

// Create a user
async function createUser(name, email) {
  const res = await fetch(`${BASE_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email }),
  });

  if (res.status === 201) {
    const user = await res.json();
    console.log("Created:", user);
    console.log("Location:", res.headers.get("Location"));
    return user;
  }

  const error = await res.json();
  console.error("Error:", error);
}

// List users with pagination
async function listUsers(page = 1, perPage = 20) {
  const res = await fetch(`${BASE_URL}/users?page=${page}&per_page=${perPage}`);
  const data = await res.json();
  console.log("Users:", data.data);
  console.log("Pagination:", data.pagination);
  return data;
}

// Get single user
async function getUser(id) {
  const res = await fetch(`${BASE_URL}/users/${id}`);
  if (res.status === 404) {
    console.log("User not found");
    return null;
  }
  return await res.json();
}

// Update user
async function updateUser(id, data) {
  const res = await fetch(`${BASE_URL}/users/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return await res.json();
}

// Delete user
async function deleteUser(id) {
  const res = await fetch(`${BASE_URL}/users/${id}`, { method: "DELETE" });
  return res.status === 204;
}

// Usage
const user = await createUser("Ankit", "ankit@example.com");
await listUsers(1, 10);
await updateUser(user.id, { name: "Ankit Kumar", email: "ankit@example.com" });
await deleteUser(user.id);
```
