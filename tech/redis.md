# Redis

## What is Redis
```
overview:
  full_name: Remote Dictionary Server
  type: In-memory data structure store
  use_as:
    - Database
    - Cache
    - Message broker
    - Streaming engine
  written_in: C
  license: BSD
  default_port: 6379
  protocol: RESP (Redis Serialization Protocol)

key_features:
  - Sub-millisecond latency (in-memory)
  - Rich data structures (strings, hashes, lists, sets, sorted sets, streams)
  - Built-in replication and clustering
  - Lua scripting support
  - Pub/Sub messaging
  - TTL-based key expiration
  - Transactions with MULTI/EXEC
  - Persistence options (RDB snapshots, AOF logs)
```

## When to Use Redis
```
use_cases:
  caching:
    description: Cache database queries, API responses, session data
    why: Reduces load on primary DB, sub-ms reads
    example: Store user profile after first DB fetch, serve from Redis on repeat requests

  session_store:
    description: Store user sessions for web applications
    why: Fast reads, built-in TTL for auto-expiry
    example: Express.js session middleware backed by Redis

  rate_limiting:
    description: Limit API requests per user/IP
    why: Atomic INCR + EXPIRE makes counting trivial
    example: Allow 100 requests per minute per API key

  leaderboards:
    description: Real-time ranking systems
    why: Sorted sets maintain order automatically
    example: Game leaderboard with ZADD and ZRANGE

  real_time_analytics:
    description: Counting, HyperLogLog for unique visitors
    why: Atomic operations, HyperLogLog uses ~12KB for billions of items

  pub_sub:
    description: Real-time messaging between services
    why: Built-in, lightweight, fire-and-forget

  distributed_locks:
    description: Coordinate access across microservices
    why: SET NX EX provides atomic lock acquisition

  queues:
    description: Simple job/task queues
    why: LPUSH/BRPOP gives reliable FIFO queue
    example: Background job processing with BullMQ
```

## Data Structures
```
data_structures:

  string:
    description: Binary-safe string, up to 512MB
    commands:
      SET: "SET key value [EX seconds] [NX|XX]"
      GET: "GET key"
      INCR: "INCR key           # atomic increment"
      MSET: "MSET k1 v1 k2 v2   # set multiple"
      MGET: "MGET k1 k2          # get multiple"
    use_case: Counters, caching simple values, flags

  hash:
    description: Field-value pairs under one key (like a mini object)
    commands:
      HSET: "HSET user:1 name 'Ankit' age 25"
      HGET: "HGET user:1 name"
      HGETALL: "HGETALL user:1"
      HDEL: "HDEL user:1 age"
      HINCRBY: "HINCRBY user:1 age 1"
    use_case: User profiles, product details, configs

  list:
    description: Ordered collection of strings (linked list)
    commands:
      LPUSH: "LPUSH queue job1 job2"
      RPUSH: "RPUSH queue job3"
      LPOP: "LPOP queue"
      RPOP: "RPOP queue"
      BRPOP: "BRPOP queue 30    # blocking pop, 30s timeout"
      LRANGE: "LRANGE queue 0 -1 # get all elements"
      LLEN: "LLEN queue"
    use_case: Message queues, activity feeds, recent items

  set:
    description: Unordered unique strings
    commands:
      SADD: "SADD tags 'go' 'redis' 'docker'"
      SMEMBERS: "SMEMBERS tags"
      SISMEMBER: "SISMEMBER tags 'go'"
      SINTER: "SINTER tags1 tags2   # intersection"
      SUNION: "SUNION tags1 tags2   # union"
      SDIFF: "SDIFF tags1 tags2    # difference"
    use_case: Tags, unique visitors, social graph (friends)

  sorted_set:
    description: Set with a score per member, sorted by score
    commands:
      ZADD: "ZADD leaderboard 100 'player1' 200 'player2'"
      ZRANGE: "ZRANGE leaderboard 0 -1 WITHSCORES"
      ZREVRANGE: "ZREVRANGE leaderboard 0 9  # top 10"
      ZRANK: "ZRANK leaderboard 'player1'"
      ZINCRBY: "ZINCRBY leaderboard 50 'player1'"
      ZRANGEBYSCORE: "ZRANGEBYSCORE leaderboard 100 300"
    use_case: Leaderboards, priority queues, time-series indexes

  stream:
    description: Append-only log (like Kafka topics)
    commands:
      XADD: "XADD mystream * sensor_id 1 temp 25.5"
      XREAD: "XREAD COUNT 10 BLOCK 5000 STREAMS mystream 0"
      XRANGE: "XRANGE mystream - +"
      XGROUP_CREATE: "XGROUP CREATE mystream grp1 $ MKSTREAM"
      XREADGROUP: "XREADGROUP GROUP grp1 consumer1 COUNT 1 STREAMS mystream >"
      XACK: "XACK mystream grp1 <message_id>"
    use_case: Event sourcing, activity logs, message streaming
```

## Essential Commands
```
commands:

  key_management:
    KEYS: "KEYS pattern        # find keys (avoid in prod, use SCAN)"
    SCAN: "SCAN 0 MATCH user:* COUNT 100"
    EXISTS: "EXISTS key"
    DEL: "DEL key1 key2"
    UNLINK: "UNLINK key          # async delete"
    EXPIRE: "EXPIRE key 3600     # TTL in seconds"
    TTL: "TTL key              # remaining TTL (-1=no expiry, -2=not found)"
    PERSIST: "PERSIST key          # remove TTL"
    TYPE: "TYPE key"
    RENAME: "RENAME oldkey newkey"

  transactions:
    MULTI: "MULTI                # start transaction"
    EXEC: "EXEC                 # execute queued commands"
    DISCARD: "DISCARD              # cancel transaction"
    WATCH: "WATCH key            # optimistic locking"
    example: |
      MULTI
      SET balance:1 900
      SET balance:2 1100
      EXEC

  pub_sub:
    SUBSCRIBE: "SUBSCRIBE channel1 channel2"
    PUBLISH: "PUBLISH channel1 'hello subscribers'"
    PSUBSCRIBE: "PSUBSCRIBE news.*   # pattern subscribe"
    UNSUBSCRIBE: "UNSUBSCRIBE channel1"

  server:
    INFO: "INFO                 # server stats"
    DBSIZE: "DBSIZE               # total key count"
    FLUSHDB: "FLUSHDB              # delete all keys in current DB"
    CONFIG_GET: "CONFIG GET maxmemory"
    CONFIG_SET: "CONFIG SET maxmemory 256mb"
    SLOWLOG: "SLOWLOG GET 10       # last 10 slow queries"
```

## Persistence
```
persistence:

  rdb_snapshots:
    description: Point-in-time snapshots of dataset
    config: |
      save 900 1      # snapshot if 1 key changed in 900s
      save 300 10     # snapshot if 10 keys changed in 300s
      save 60 10000   # snapshot if 10000 keys changed in 60s
      dbfilename dump.rdb
    pros:
      - Compact single file, great for backups
      - Fast restart (load RDB file)
    cons:
      - Data loss between snapshots

  aof_append_only_file:
    description: Logs every write operation
    config: |
      appendonly yes
      appendfsync everysec   # options: always, everysec, no
      appendfilename appendonly.aof
    pros:
      - Minimal data loss (1 second max with everysec)
      - Human-readable log
    cons:
      - Larger file size than RDB
      - Slower restart

  recommended: Use both RDB + AOF for production
```

## Eviction Policies
```
eviction_policies:
  description: What happens when Redis hits maxmemory limit

  policies:
    noeviction: "Return error on write (default)"
    allkeys-lru: "Evict least recently used key (most common)"
    allkeys-lfu: "Evict least frequently used key"
    allkeys-random: "Evict random key"
    volatile-lru: "LRU among keys with TTL set"
    volatile-lfu: "LFU among keys with TTL set"
    volatile-random: "Random among keys with TTL set"
    volatile-ttl: "Evict keys with shortest TTL"

  config: |
    maxmemory 256mb
    maxmemory-policy allkeys-lru
```

## Replication & Clustering
```
architecture:

  replication:
    description: Master-replica setup for read scaling and failover
    config_replica: "REPLICAOF master_host 6379"
    features:
      - Async replication by default
      - Replicas are read-only
      - One master can have multiple replicas

  sentinel:
    description: High availability solution - monitors and auto-failover
    features:
      - Monitors master and replicas
      - Automatic failover if master goes down
      - Notifies clients of topology changes
    config: |
      sentinel monitor mymaster 127.0.0.1 6379 2
      sentinel down-after-milliseconds mymaster 5000
      sentinel failover-timeout mymaster 60000

  cluster:
    description: Horizontal sharding across multiple nodes
    features:
      - Data auto-sharded across 16384 hash slots
      - Each node owns a subset of slots
      - Built-in replication per shard
      - Minimum 3 master nodes recommended
    create: "redis-cli --cluster create node1:6379 node2:6379 node3:6379 --cluster-replicas 1"
```

## Example - Node.js Application
```
example_nodejs:
  description: Express API with Redis caching

  install: "npm install express ioredis"

  code: |
    const express = require('express');
    const Redis = require('ioredis');

    const app = express();
    const redis = new Redis({ host: '127.0.0.1', port: 6379 });

    // Cache middleware
    async function cacheMiddleware(req, res, next) {
      const key = `cache:${req.originalUrl}`;
      const cached = await redis.get(key);
      if (cached) {
        return res.json(JSON.parse(cached));
      }
      res.sendResponse = res.json;
      res.json = (body) => {
        redis.setex(key, 3600, JSON.stringify(body)); // cache 1 hour
        res.sendResponse(body);
      };
      next();
    }

    // Rate limiter middleware
    async function rateLimiter(req, res, next) {
      const ip = req.ip;
      const key = `ratelimit:${ip}`;
      const current = await redis.incr(key);
      if (current === 1) await redis.expire(key, 60);
      if (current > 100) {
        return res.status(429).json({ error: 'Too many requests' });
      }
      next();
    }

    app.use(rateLimiter);

    app.get('/api/users/:id', cacheMiddleware, async (req, res) => {
      // Simulate DB call
      const user = { id: req.params.id, name: 'Ankit', role: 'dev' };
      res.json(user);
    });

    // Leaderboard example
    app.post('/api/score', express.json(), async (req, res) => {
      const { player, score } = req.body;
      await redis.zadd('leaderboard', score, player);
      const rank = await redis.zrevrank('leaderboard', player);
      res.json({ player, score, rank: rank + 1 });
    });

    app.get('/api/leaderboard', async (req, res) => {
      const top10 = await redis.zrevrange('leaderboard', 0, 9, 'WITHSCORES');
      const result = [];
      for (let i = 0; i < top10.length; i += 2) {
        result.push({ player: top10[i], score: Number(top10[i + 1]) });
      }
      res.json(result);
    });

    app.listen(3000, () => console.log('Server on :3000'));

  run: "node app.js"
```

## Example - Go Application
```
example_go:
  description: Session store and pub/sub with go-redis

  install: "go get github.com/redis/go-redis/v9"

  code: |
    package main

    import (
        "context"
        "fmt"
        "time"
        "github.com/redis/go-redis/v9"
    )

    var ctx = context.Background()

    func main() {
        rdb := redis.NewClient(&redis.Options{
            Addr: "localhost:6379",
        })
        defer rdb.Close()

        // Basic SET/GET
        rdb.Set(ctx, "greeting", "hello redis", 10*time.Minute)
        val, _ := rdb.Get(ctx, "greeting").Result()
        fmt.Println(val)

        // Hash - store user
        rdb.HSet(ctx, "user:1", map[string]interface{}{
            "name": "Ankit", "lang": "Go", "exp": 3,
        })
        user, _ := rdb.HGetAll(ctx, "user:1").Result()
        fmt.Println(user)

        // Sorted Set - leaderboard
        rdb.ZAdd(ctx, "scores", redis.Z{Score: 100, Member: "alice"})
        rdb.ZAdd(ctx, "scores", redis.Z{Score: 200, Member: "bob"})
        top, _ := rdb.ZRevRangeWithScores(ctx, "scores", 0, 4).Result()
        for _, z := range top {
            fmt.Printf("%s: %.0f\n", z.Member, z.Score)
        }

        // Pub/Sub
        go func() {
            sub := rdb.Subscribe(ctx, "notifications")
            ch := sub.Channel()
            for msg := range ch {
                fmt.Printf("Received on %s: %s\n", msg.Channel, msg.Payload)
            }
        }()

        time.Sleep(time.Second)
        rdb.Publish(ctx, "notifications", "deployment started")
        time.Sleep(time.Second)
    }

  run: "go run main.go"
```

## Docker Setup
```
docker:

  single_instance:
    command: "docker run -d --name redis -p 6379:6379 redis:7-alpine"
    with_persistence: "docker run -d --name redis -p 6379:6379 -v redis_data:/data redis:7-alpine redis-server --appendonly yes"

  docker_compose:
    file: |
      version: '3.8'
      services:
        redis:
          image: redis:7-alpine
          ports:
            - "6379:6379"
          command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
          volumes:
            - redis_data:/data
          restart: unless-stopped

        redis-insight:
          image: redislabs/redisinsight:latest
          ports:
            - "8001:8001"
          depends_on:
            - redis
      volumes:
        redis_data:

  connect: "docker exec -it redis redis-cli"
```

## Best Practices
```
best_practices:
  naming_keys:
    - "Use colon-separated namespaces: user:1:profile, order:123:items"
    - "Keep keys short but descriptive"
    - "Avoid KEYS command in production, use SCAN"

  performance:
    - "Use pipelining for bulk operations (batch commands)"
    - "Use MGET/MSET instead of multiple GET/SET"
    - "Set TTL on all cache keys to prevent memory bloat"
    - "Use UNLINK instead of DEL for large keys (async delete)"

  security:
    - "Always set a password: requirepass <password>"
    - "Bind to specific IPs, never 0.0.0.0 in prod"
    - "Disable dangerous commands: rename-command FLUSHALL ''"
    - "Use TLS for connections over network"
    - "Run Redis as non-root user"

  monitoring:
    - "Use INFO command for stats"
    - "Monitor SLOWLOG for slow queries"
    - "Track memory usage with INFO memory"
    - "Set up alerts for maxmemory threshold"
```
