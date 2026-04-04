# Caching

## What is Caching
```
overview:
  definition: |
    Caching is the process of storing copies of data in a temporary
    high-speed storage layer so future requests for that data are
    served faster than fetching from the original source.
  purpose:
    - Reduce latency (serve from memory instead of disk/network)
    - Reduce load on origin servers and databases
    - Improve throughput and user experience
  layers:
    - Browser cache (client-side)
    - CDN cache (edge servers)
    - Application cache (in-process memory)
    - Distributed cache (Redis, Memcached)
    - Database cache (query cache, buffer pool)
```

## Caching Strategies
```
strategies:

  cache_aside:
    also_called: Lazy loading
    how_it_works: |
      1. Application checks cache first
      2. If cache hit -> return cached data
      3. If cache miss -> fetch from DB, store in cache, return
    pros:
      - Only caches data that is actually requested
      - Cache failure doesn't break the system (falls back to DB)
    cons:
      - First request is always slow (cache miss)
      - Data can become stale if DB is updated directly
    best_for: Read-heavy workloads, general-purpose caching

  read_through:
    how_it_works: |
      1. Application reads from cache
      2. On cache miss, the cache itself fetches from DB
      3. Cache stores the data and returns to application
    difference_from_cache_aside: Cache library handles the DB fetch, not application code
    pros:
      - Simpler application code
      - Cache always stays in sync with reads
    cons:
      - Cache library must know how to fetch from data source
    best_for: When using a cache library that supports data loading

  write_through:
    how_it_works: |
      1. Application writes to cache
      2. Cache synchronously writes to DB
      3. Write is confirmed only after both succeed
    pros:
      - Cache is always consistent with DB
      - No stale data
    cons:
      - Higher write latency (two writes on every update)
      - Cache may store data that is never read
    best_for: Data that is read frequently after being written

  write_behind:
    also_called: Write-back
    how_it_works: |
      1. Application writes to cache
      2. Cache acknowledges immediately
      3. Cache asynchronously writes to DB in batches
    pros:
      - Very fast writes (only to cache)
      - Batching reduces DB load
    cons:
      - Risk of data loss if cache crashes before flushing to DB
      - Eventual consistency between cache and DB
    best_for: Write-heavy workloads where slight delay is acceptable
```

## Cache Invalidation
```
invalidation:
  description: |
    "There are only two hard things in CS: cache invalidation and naming things."
    Cache invalidation ensures stale data is removed or updated.

  strategies:
    ttl:
      description: Time-To-Live - cache entry expires after a set duration
      example: "SET key value EX 3600  # expires in 1 hour"
      trade_off: Simple but data can be stale until TTL expires
      common_values:
        static_assets: "1 day to 1 year"
        api_responses: "30 seconds to 5 minutes"
        user_sessions: "15 minutes to 24 hours"

    event_based:
      description: Invalidate cache when data changes (publish event)
      how: "On DB update -> publish 'user:123:updated' -> cache deletes key"
      trade_off: Real-time freshness but adds complexity

    version_based:
      description: Append version or hash to cache key
      example: "cache:user:123:v5 -> new version means new key"
      trade_off: Old versions eventually expire via TTL

    write_invalidate:
      description: Delete cache entry on every write
      how: "On DB update -> DELETE cache key -> next read refills cache"
      trade_off: Simple, guarantees fresh data on next read

    write_update:
      description: Update cache entry on every write
      how: "On DB update -> SET cache key with new value"
      trade_off: Cache always fresh, but extra write on every update
```

## HTTP Cache Headers
```
http_caching:
  description: Browsers and CDNs use HTTP headers to decide what to cache and for how long

  headers:
    cache_control:
      description: Primary header for caching directives
      directives:
        public: "Any cache (browser, CDN, proxy) can store it"
        private: "Only browser can cache, not CDN/proxy"
        no-cache: "Must revalidate with server before using cached copy"
        no-store: "Do not cache at all (sensitive data)"
        max-age: "Cache is fresh for N seconds"
        s-maxage: "Like max-age but for shared caches (CDN)"
        must-revalidate: "Once stale, must check with origin"
        immutable: "Content will never change, don't revalidate"
      examples:
        static_assets: "Cache-Control: public, max-age=31536000, immutable"
        api_response: "Cache-Control: private, max-age=60"
        sensitive_data: "Cache-Control: no-store"
        html_page: "Cache-Control: public, no-cache"

    etag:
      description: Unique identifier for a specific version of a resource
      how_it_works: |
        1. Server sends: ETag: "abc123"
        2. Browser caches response with ETag
        3. Next request sends: If-None-Match: "abc123"
        4. If unchanged -> 304 Not Modified (no body)
        5. If changed -> 200 OK with new ETag and body
      types:
        strong: '"abc123" - byte-for-byte identical'
        weak: 'W/"abc123" - semantically equivalent'

    last_modified:
      description: Timestamp when the resource was last changed
      how_it_works: |
        1. Server sends: Last-Modified: Mon, 01 Jan 2026 00:00:00 GMT
        2. Next request sends: If-Modified-Since: Mon, 01 Jan 2026 00:00:00 GMT
        3. If unchanged -> 304 Not Modified
        4. If changed -> 200 OK with new Last-Modified

    pragma:
      description: "Legacy HTTP/1.0 header, use Cache-Control instead"
      example: "Pragma: no-cache (equivalent to Cache-Control: no-cache)"
```

## CDN Caching
```
cdn_caching:
  description: Content Delivery Network caches content at edge servers worldwide

  how_it_works: |
    1. User requests resource -> CDN edge server closest to user
    2. If cached at edge -> serve directly (cache hit)
    3. If not cached -> fetch from origin server, cache at edge, serve
    4. Subsequent requests from same region served from edge

  what_to_cache:
    - Static assets (images, CSS, JS, fonts)
    - HTML pages (if content doesn't change per user)
    - API responses (with proper cache headers)
    - Video and media files

  cache_key: "Usually: HTTP method + URL + selected headers (Vary)"

  purging:
    description: Force CDN to remove cached content
    methods:
      - "Purge by URL (invalidate specific resource)"
      - "Purge by tag/surrogate key (invalidate group of resources)"
      - "Purge all (nuclear option)"
    tools:
      cloudflare: "API call or dashboard purge"
      aws_cloudfront: "Create invalidation: /* or /path/to/file"
      fastly: "Instant purge via surrogate keys"

  popular_cdns:
    - Cloudflare
    - AWS CloudFront
    - Fastly
    - Akamai
    - Google Cloud CDN
```

## Browser Caching
```
browser_caching:
  description: Browser stores responses locally to avoid re-fetching

  types:
    memory_cache:
      storage: RAM
      lifetime: Until tab is closed
      used_for: Resources needed multiple times on same page

    disk_cache:
      storage: Hard drive
      lifetime: Based on Cache-Control / Expires headers
      used_for: Resources across page navigations

    service_worker_cache:
      storage: Managed by service worker
      lifetime: Until explicitly cleared
      used_for: Offline support, custom caching strategies

  cache_busting:
    description: Force browser to fetch new version of cached asset
    techniques:
      query_string: "style.css?v=2 or style.css?t=1234567890"
      filename_hash: "style.a1b2c3d4.css (better, immutable-friendly)"
      build_tools: "Webpack, Vite auto-generate hashed filenames"
```

## Cache Stampede
```
cache_stampede:
  also_called: Thundering herd, cache avalanche
  description: |
    When a popular cache key expires, many concurrent requests
    simultaneously miss the cache and hit the database, potentially
    overwhelming it.

  scenario: |
    1. Popular key (e.g., homepage data) expires
    2. 1000 requests arrive simultaneously
    3. All 1000 see cache miss
    4. All 1000 query the database
    5. Database gets overwhelmed

  solutions:
    locking:
      description: Only one request fetches from DB, others wait
      how: "Use distributed lock (Redis SETNX), first request rebuilds cache"

    early_expiration:
      description: Probabilistically refresh before actual TTL expires
      how: "If remaining TTL < random threshold, refresh in background"

    cache_warming:
      description: Pre-populate cache before traffic hits
      how: "On deploy or schedule, fill cache with known hot keys"

    never_expire:
      description: Use background refresh instead of TTL expiration
      how: "Cache has no TTL, background job updates it periodically"

    request_coalescing:
      description: Collapse duplicate in-flight requests into one
      how: "singleflight pattern in Go - only one goroutine fetches, others wait"
```

## Cache Warming
```
cache_warming:
  description: Pre-populating cache with data before users request it

  when_to_use:
    - After a deployment (caches are cold)
    - After cache flush or Redis restart
    - Before a known traffic spike (product launch, sale)
    - When migrating to a new cache cluster

  strategies:
    on_deploy:
      description: Run a warming script as part of deployment
      example: "Fetch top 1000 products and store in cache"

    lazy_background:
      description: Background workers gradually warm cache
      example: "Worker reads most-accessed keys from logs, pre-fetches them"

    mirrored_traffic:
      description: Replay production traffic to warm new cache
      example: "Shadow traffic to new Redis instance before cutover"
```

## Example - Redis Caching in Go
```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "sync"
    "time"

    "github.com/redis/go-redis/v9"
    "golang.org/x/sync/singleflight"
)

var (
    ctx = context.Background()
    rdb *redis.Client
    sf  singleflight.Group
)

type Product struct {
    ID    string  `json:"id"`
    Name  string  `json:"name"`
    Price float64 `json:"price"`
}

func init() {
    rdb = redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
}

// Cache-aside pattern with singleflight to prevent stampede
func GetProduct(id string) (*Product, error) {
    cacheKey := fmt.Sprintf("product:%s", id)

    // 1. Check cache
    cached, err := rdb.Get(ctx, cacheKey).Result()
    if err == nil {
        var p Product
        json.Unmarshal([]byte(cached), &p)
        return &p, nil
    }

    // 2. Cache miss - use singleflight to prevent stampede
    result, err, _ := sf.Do(cacheKey, func() (interface{}, error) {
        // Simulate DB fetch
        p := &Product{ID: id, Name: "Widget", Price: 29.99}

        // Store in cache with TTL
        data, _ := json.Marshal(p)
        rdb.Set(ctx, cacheKey, data, 10*time.Minute)

        return p, nil
    })

    if err != nil {
        return nil, err
    }
    return result.(*Product), nil
}

// Write-through pattern
func UpdateProduct(p *Product) error {
    // 1. Update database (simulated)
    fmt.Printf("DB updated: %s\n", p.ID)

    // 2. Update cache
    cacheKey := fmt.Sprintf("product:%s", p.ID)
    data, _ := json.Marshal(p)
    return rdb.Set(ctx, cacheKey, data, 10*time.Minute).Err()
}

// Write-invalidate pattern
func DeleteProduct(id string) error {
    // 1. Delete from database (simulated)
    fmt.Printf("DB deleted: %s\n", id)

    // 2. Invalidate cache
    cacheKey := fmt.Sprintf("product:%s", id)
    return rdb.Del(ctx, cacheKey).Err()
}

// Cache warming - preload hot keys
func WarmCache(productIDs []string) {
    var wg sync.WaitGroup
    for _, id := range productIDs {
        wg.Add(1)
        go func(id string) {
            defer wg.Done()
            GetProduct(id)
        }(id)
    }
    wg.Wait()
    fmt.Println("Cache warmed with", len(productIDs), "products")
}

func main() {
    defer rdb.Close()

    // Warm cache on startup
    WarmCache([]string{"1", "2", "3", "4", "5"})

    // Cache-aside read
    p, _ := GetProduct("1")
    fmt.Printf("Got product: %+v\n", p)

    // Write-through update
    p.Price = 39.99
    UpdateProduct(p)

    // Read again (from cache)
    p, _ = GetProduct("1")
    fmt.Printf("Updated product: %+v\n", p)
}
```

## Example - HTTP Cache Headers in Go
```go
package main

import (
    "crypto/md5"
    "fmt"
    "net/http"
    "time"
)

func staticHandler(w http.ResponseWriter, r *http.Request) {
    // Immutable static assets (use hashed filenames)
    w.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
    w.Write([]byte("static content"))
}

func apiHandler(w http.ResponseWriter, r *http.Request) {
    data := []byte(`{"users": [{"id": 1, "name": "Ankit"}]}`)

    // Generate ETag from content
    etag := fmt.Sprintf(`"%x"`, md5.Sum(data))
    w.Header().Set("ETag", etag)
    w.Header().Set("Cache-Control", "private, max-age=60")

    // Check If-None-Match
    if r.Header.Get("If-None-Match") == etag {
        w.WriteHeader(http.StatusNotModified)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    w.Write(data)
}

func sensitiveHandler(w http.ResponseWriter, r *http.Request) {
    // Never cache sensitive data
    w.Header().Set("Cache-Control", "no-store")
    w.Write([]byte("sensitive data"))
}

func main() {
    http.HandleFunc("/static/", staticHandler)
    http.HandleFunc("/api/users", apiHandler)
    http.HandleFunc("/api/account", sensitiveHandler)
    fmt.Println("Server on :8080")
    http.ListenAndServe(":8080", nil)
}
```

## Best Practices
```
best_practices:
  general:
    - "Cache the result, not the query - store computed/formatted data"
    - "Always set a TTL - prevents memory bloat from forgotten keys"
    - "Use consistent key naming: entity:id:field (e.g., user:123:profile)"
    - "Monitor cache hit rate - below 80% means your caching strategy needs work"
    - "Plan for cache failure - app should work (slower) without cache"

  invalidation:
    - "Prefer TTL + event-based invalidation together"
    - "Keep TTL short for frequently changing data (30s-5min)"
    - "Use longer TTL for rarely changing data (hours-days)"
    - "Invalidate on write, not on read"

  performance:
    - "Use pipelining for bulk cache operations"
    - "Compress large cached values (gzip/snappy)"
    - "Use local in-process cache for ultra-hot keys (sync.Map or LRU)"
    - "Layer caches: local memory -> Redis -> database"

  pitfalls:
    - "Don't cache user-specific data in shared CDN cache"
    - "Don't cache errors (negative caching) without very short TTL"
    - "Don't ignore cache stampede on high-traffic keys"
    - "Don't use cache as primary data store (it's ephemeral)"
```

## Tags
```
tags:
  - caching
  - redis
  - performance
  - http
  - cdn
  - system-design
```
