# Rate Limiting

## What is Rate Limiting
```
overview:
  definition: |
    Rate limiting controls how many requests a client can make
    to a server within a given time window. Requests beyond
    the limit are rejected (usually with HTTP 429 Too Many Requests).
  purpose:
    - Prevent abuse and DDoS attacks
    - Protect backend services from overload
    - Ensure fair usage across all clients
    - Control costs (API billing, infrastructure)
    - Meet SLA/compliance requirements

  where_to_apply:
    - API gateway (first line of defense)
    - Load balancer (Nginx, HAProxy)
    - Application middleware
    - Database query layer
    - Third-party API calls (respect their limits)

  common_identifiers:
    - IP address
    - API key
    - User ID / Auth token
    - Endpoint / Route
    - Combination (user + endpoint)
```

## Rate Limiting Algorithms
```
algorithms:

  fixed_window:
    description: Count requests in fixed time windows (e.g., per minute)
    how_it_works: |
      1. Divide time into fixed windows (e.g., 0:00-0:59, 1:00-1:59)
      2. Each window has a counter starting at 0
      3. Every request increments the counter
      4. If counter > limit, reject request
      5. Counter resets at the start of each window
    pros:
      - Simple to implement
      - Low memory (one counter per window)
    cons:
      - Burst at window boundary: 100 requests at 0:59 + 100 at 1:00 = 200 in 2 seconds
    example:
      limit: "100 requests per minute"
      window: "0:00 to 0:59"
      at_0_58: "counter = 95 -> allowed"
      at_0_59: "counter = 100 -> blocked"
      at_1_00: "counter resets to 0 -> allowed again"

  sliding_window_log:
    description: Track timestamp of each request, count within sliding window
    how_it_works: |
      1. Store timestamp of every request
      2. On new request, remove timestamps older than window
      3. Count remaining timestamps
      4. If count > limit, reject
    pros:
      - No boundary burst problem
      - Accurate rate limiting
    cons:
      - High memory usage (stores every timestamp)
    example:
      limit: "100 requests per minute"
      at_1_15_30: "Count requests from 1:14:30 to 1:15:30 -> 98 -> allowed"

  sliding_window_counter:
    description: Weighted average of current and previous window counts
    how_it_works: |
      1. Track count for current and previous fixed windows
      2. On new request, calculate weighted count:
         weighted = prev_count * (1 - elapsed/window) + current_count
      3. If weighted > limit, reject
    pros:
      - Smooths out boundary bursts
      - Low memory (two counters per key)
    cons:
      - Approximate (not perfectly accurate)
    example:
      limit: "100 requests per minute"
      prev_window_count: 84
      current_window_count: 36
      elapsed_percent: "25% into current window"
      weighted: "84 * 0.75 + 36 = 99 -> allowed"

  token_bucket:
    description: Bucket holds tokens, each request consumes one token, tokens refill at fixed rate
    how_it_works: |
      1. Bucket starts with N tokens (max capacity)
      2. Each request takes one token
      3. Tokens are added at a fixed rate (e.g., 10/sec)
      4. If no tokens available, reject request
      5. Bucket never exceeds max capacity
    pros:
      - Allows controlled bursts (up to bucket size)
      - Smooth rate limiting
      - Used by AWS, Stripe, many APIs
    cons:
      - Slightly more complex to implement
    parameters:
      bucket_size: "Maximum burst size (e.g., 100)"
      refill_rate: "Tokens added per second (e.g., 10)"
    example:
      bucket_size: 10
      refill_rate: "1 token/sec"
      scenario: "10 requests instantly (burst) -> bucket empty -> 1 req/sec after"

  leaky_bucket:
    description: Requests enter a bucket and are processed at a fixed rate
    how_it_works: |
      1. Requests are added to a queue (bucket)
      2. Queue is processed at a fixed rate
      3. If queue is full, new requests are rejected
    pros:
      - Produces a perfectly smooth output rate
      - Good for APIs that need constant throughput
    cons:
      - No burst tolerance (even valid bursts are queued)
      - Adds latency (requests wait in queue)
    difference_from_token_bucket: |
      Token bucket: controls input rate (allows bursts)
      Leaky bucket: controls output rate (smooth processing)
```

## Rate Limiting at Different Layers
```
layers:

  api_gateway:
    description: First line of defense, before requests hit application
    tools:
      - "Kong: rate-limiting plugin per consumer/route"
      - "AWS API Gateway: usage plans with throttling"
      - "Nginx: limit_req module"
    pros: Protects all downstream services, centralized config
    example: "100 requests/min per API key across all endpoints"

  load_balancer:
    description: Rate limit at network edge
    tools:
      - "Nginx: limit_req_zone + limit_req"
      - "HAProxy: stick-table with rate tracking"
      - "AWS ALB: not built-in (use WAF)"
    pros: Very fast, handles before application code runs

  application:
    description: Rate limit within application code (middleware)
    tools:
      - "Go: custom middleware with Redis"
      - "Express.js: express-rate-limit package"
      - "Django: django-ratelimit"
    pros: Fine-grained control (per endpoint, per user, per action)
    example: "POST /api/login: 5 attempts per 15 minutes per IP"

  distributed:
    description: Shared rate limit across multiple application instances
    requires: Central store (Redis, Memcached)
    why: Each instance needs to see the same counters
    tools:
      - "Redis: INCR + EXPIRE (simple)"
      - "Redis: Lua script (atomic, accurate)"
      - "Redis Cell: native rate limiting module"
```

## HTTP Response Headers
```
response_headers:
  description: Inform clients about their rate limit status

  standard_headers:
    RateLimit-Limit: "Maximum requests allowed in window"
    RateLimit-Remaining: "Requests remaining in current window"
    RateLimit-Reset: "Unix timestamp when the window resets"
    Retry-After: "Seconds to wait before retrying (on 429)"

  example_response:
    status: "429 Too Many Requests"
    headers:
      RateLimit-Limit: "100"
      RateLimit-Remaining: "0"
      RateLimit-Reset: "1672531260"
      Retry-After: "30"
    body: '{"error": "rate limit exceeded", "retry_after": 30}'
```

## Example - Go Rate Limiting Middleware
```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "sync"
    "time"
)

// In-memory token bucket rate limiter
type TokenBucket struct {
    tokens     float64
    maxTokens  float64
    refillRate float64 // tokens per second
    lastRefill time.Time
    mu         sync.Mutex
}

func NewTokenBucket(maxTokens, refillRate float64) *TokenBucket {
    return &TokenBucket{
        tokens:     maxTokens,
        maxTokens:  maxTokens,
        refillRate: refillRate,
        lastRefill: time.Now(),
    }
}

func (tb *TokenBucket) Allow() bool {
    tb.mu.Lock()
    defer tb.mu.Unlock()

    // Refill tokens based on elapsed time
    now := time.Now()
    elapsed := now.Sub(tb.lastRefill).Seconds()
    tb.tokens += elapsed * tb.refillRate
    if tb.tokens > tb.maxTokens {
        tb.tokens = tb.maxTokens
    }
    tb.lastRefill = now

    // Try to consume a token
    if tb.tokens >= 1 {
        tb.tokens--
        return true
    }
    return false
}

// Per-client rate limiter
type RateLimiter struct {
    clients map[string]*TokenBucket
    mu      sync.RWMutex
    max     float64
    rate    float64
}

func NewRateLimiter(maxTokens, refillRate float64) *RateLimiter {
    rl := &RateLimiter{
        clients: make(map[string]*TokenBucket),
        max:     maxTokens,
        rate:    refillRate,
    }
    // Cleanup stale entries every 5 minutes
    go rl.cleanup()
    return rl
}

func (rl *RateLimiter) GetBucket(key string) *TokenBucket {
    rl.mu.RLock()
    bucket, exists := rl.clients[key]
    rl.mu.RUnlock()

    if exists {
        return bucket
    }

    rl.mu.Lock()
    defer rl.mu.Unlock()
    // Double-check after acquiring write lock
    if bucket, exists = rl.clients[key]; exists {
        return bucket
    }
    bucket = NewTokenBucket(rl.max, rl.rate)
    rl.clients[key] = bucket
    return bucket
}

func (rl *RateLimiter) cleanup() {
    for range time.Tick(5 * time.Minute) {
        rl.mu.Lock()
        for key, bucket := range rl.clients {
            bucket.mu.Lock()
            if time.Since(bucket.lastRefill) > 10*time.Minute {
                delete(rl.clients, key)
            }
            bucket.mu.Unlock()
        }
        rl.mu.Unlock()
    }
}

// Middleware
func RateLimitMiddleware(limiter *RateLimiter) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            key := r.RemoteAddr // or extract API key, user ID, etc.
            bucket := limiter.GetBucket(key)

            if !bucket.Allow() {
                w.Header().Set("Retry-After", "1")
                w.Header().Set("RateLimit-Limit", fmt.Sprintf("%.0f", limiter.max))
                w.Header().Set("RateLimit-Remaining", "0")
                http.Error(w, `{"error": "rate limit exceeded"}`, http.StatusTooManyRequests)
                return
            }

            w.Header().Set("RateLimit-Limit", fmt.Sprintf("%.0f", limiter.max))
            w.Header().Set("RateLimit-Remaining", fmt.Sprintf("%.0f", bucket.tokens))
            next.ServeHTTP(w, r)
        })
    }
}

func main() {
    // 10 requests max, refill 2 tokens per second
    limiter := NewRateLimiter(10, 2)

    mux := http.NewServeMux()
    mux.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"message": "success"}`))
    })

    handler := RateLimitMiddleware(limiter)(mux)
    log.Println("Server on :8080")
    http.ListenAndServe(":8080", handler)
}
```

## Example - Redis Distributed Rate Limiter
```go
package main

import (
    "context"
    "fmt"
    "net/http"
    "time"

    "github.com/redis/go-redis/v9"
)

var (
    ctx = context.Background()
    rdb *redis.Client
)

func init() {
    rdb = redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
}

// Sliding window counter using Redis Lua script (atomic)
var slidingWindowScript = redis.NewScript(`
    local key = KEYS[1]
    local window = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    -- Remove expired entries
    redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

    -- Count current entries
    local count = redis.call('ZCARD', key)

    if count < limit then
        -- Add current request
        redis.call('ZADD', key, now, now .. '-' .. math.random(1000000))
        redis.call('EXPIRE', key, window)
        return 0  -- allowed
    else
        return 1  -- rejected
    end
`)

func RedisRateLimitMiddleware(limit int, window time.Duration) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            key := fmt.Sprintf("ratelimit:%s", r.RemoteAddr)
            now := time.Now().UnixMilli()

            result, err := slidingWindowScript.Run(ctx, rdb, []string{key},
                window.Milliseconds(), limit, now,
            ).Int()

            if err != nil {
                // If Redis is down, allow request (fail open)
                next.ServeHTTP(w, r)
                return
            }

            if result == 1 {
                w.Header().Set("Retry-After", fmt.Sprintf("%d", int(window.Seconds())))
                http.Error(w, `{"error": "rate limit exceeded"}`, http.StatusTooManyRequests)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte(`{"message": "success"}`))
    })

    // 100 requests per minute
    handler := RedisRateLimitMiddleware(100, time.Minute)(mux)
    fmt.Println("Server on :8080")
    http.ListenAndServe(":8080", handler)
}
```

## Example - Express.js Rate Limiter
```javascript
const express = require('express');
const Redis = require('ioredis');

const app = express();
const redis = new Redis({ host: '127.0.0.1', port: 6379 });

// Fixed window rate limiter middleware
function rateLimiter({ limit = 100, windowSec = 60 } = {}) {
    return async (req, res, next) => {
        const key = `ratelimit:${req.ip}:${Math.floor(Date.now() / 1000 / windowSec)}`;

        const current = await redis.incr(key);
        if (current === 1) {
            await redis.expire(key, windowSec);
        }

        res.set('RateLimit-Limit', String(limit));
        res.set('RateLimit-Remaining', String(Math.max(0, limit - current)));

        if (current > limit) {
            res.set('Retry-After', String(windowSec));
            return res.status(429).json({ error: 'Too many requests' });
        }

        next();
    };
}

// Apply globally: 100 req/min
app.use(rateLimiter({ limit: 100, windowSec: 60 }));

// Stricter limit on login: 5 req/15min
app.post('/api/login', rateLimiter({ limit: 5, windowSec: 900 }), (req, res) => {
    res.json({ token: 'jwt-token-here' });
});

app.get('/api/data', (req, res) => {
    res.json({ message: 'success' });
});

app.listen(3000, () => console.log('Server on :3000'));
```

## Best Practices
```
best_practices:
  design:
    - "Rate limit by multiple dimensions (IP + user + endpoint)"
    - "Use different limits for different endpoints (login stricter than read)"
    - "Return proper 429 status with Retry-After header"
    - "Include rate limit headers in every response (not just rejections)"
    - "Fail open if rate limiter store (Redis) is down - don't break the whole API"

  implementation:
    - "Use atomic operations (Redis Lua scripts) to avoid race conditions"
    - "Token bucket for APIs that should allow bursts"
    - "Sliding window for strict per-second/minute enforcement"
    - "Fixed window only for simple low-stakes use cases"

  distributed:
    - "Use Redis for shared state across multiple instances"
    - "Consider eventual consistency - slight over-limit is usually acceptable"
    - "Set TTL on all rate limit keys to prevent memory leaks"
    - "Use Redis Cluster for high availability"

  client_side:
    - "Implement exponential backoff when receiving 429"
    - "Respect Retry-After header"
    - "Cache rate limit state locally to avoid unnecessary requests"
```

## Tags
```
tags:
  - rate-limiting
  - api-design
  - middleware
  - redis
  - system-design
  - security
```
