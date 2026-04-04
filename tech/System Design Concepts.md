# System Design Concepts

## What is System Design
```
overview:
  definition: |
    System design is the process of defining the architecture, components,
    modules, interfaces, and data flow of a system to satisfy specified
    requirements. It bridges the gap between business needs and technical
    implementation at scale.
  why_it_matters:
    - Systems must handle millions of users and petabytes of data
    - Poor design leads to downtime, data loss, and spiraling costs
    - Good design enables scaling, reliability, and maintainability
  core_pillars:
    - Scalability (handle growth)
    - Availability (stay online)
    - Consistency (correct data)
    - Performance (fast responses)
    - Durability (don't lose data)
```

## Scalability
```
scalability:
  definition: |
    The ability of a system to handle increased load by adding resources.
    Load can be more users, more data, more requests, or more complexity.

  vertical_scaling:
    also_called: Scaling up
    how: Add more CPU, RAM, disk, or faster hardware to a single machine
    pros:
      - Simple, no code changes needed
      - No distributed system complexity
      - ACID transactions remain easy
    cons:
      - Hardware limits (you can't add infinite RAM)
      - Single point of failure
      - Expensive (high-end machines cost disproportionately more)
      - Downtime during upgrades
    ceiling: "Largest single machines top out around 24TB RAM, 448 vCPUs (AWS u-24tb1.metal)"

  horizontal_scaling:
    also_called: Scaling out
    how: Add more machines to distribute the load
    pros:
      - Near-infinite scaling potential
      - Redundancy (one machine fails, others continue)
      - Cost-effective (commodity hardware)
      - No downtime for scaling
    cons:
      - Distributed system complexity (networking, consistency, coordination)
      - Application must be designed for it (stateless, partitioned data)
      - Harder debugging and monitoring
    requires:
      - Load balancer to distribute traffic
      - Stateless application design (or sticky sessions)
      - Distributed data storage strategy

  diagram: |
    Vertical Scaling:
    +-----------+       +===============+
    | Server    |  -->  | BIGGER Server |
    | 4 CPU     |       | 64 CPU        |
    | 16GB RAM  |       | 512GB RAM     |
    +-----------+       +===============+

    Horizontal Scaling:
    +-----------+       +-----------+ +-----------+ +-----------+
    | Server    |  -->  | Server 1  | | Server 2  | | Server 3  |
    | (alone)   |       +-----------+ +-----------+ +-----------+
    +-----------+              ^             ^             ^
                               |             |             |
                          +----+-------------+-------------+----+
                          |           Load Balancer              |
                          +--------------------------------------+
```

## Availability
```
availability:
  definition: |
    The percentage of time a system is operational and accessible.
    Measured in "nines" - each additional 9 dramatically reduces allowed downtime.

  nines_table:
    two_nines:
      percentage: "99%"
      downtime_per_year: "3.65 days"
      downtime_per_month: "7.31 hours"
    three_nines:
      percentage: "99.9%"
      downtime_per_year: "8.77 hours"
      downtime_per_month: "43.8 minutes"
    four_nines:
      percentage: "99.99%"
      downtime_per_year: "52.6 minutes"
      downtime_per_month: "4.38 minutes"
    five_nines:
      percentage: "99.999%"
      downtime_per_year: "5.26 minutes"
      downtime_per_month: "26.3 seconds"

  how_to_achieve:
    - Redundancy (no single point of failure)
    - Load balancing across multiple servers
    - Health checks and automatic failover
    - Multi-region / multi-AZ deployment
    - Graceful degradation (serve partial results if one service is down)
    - Circuit breakers to prevent cascade failures

  calculating_combined_availability: |
    Services in sequence (both must work):
      A(total) = A(service1) x A(service2)
      99.9% x 99.9% = 99.8%

    Services in parallel (either works):
      A(total) = 1 - (1 - A(s1)) x (1 - A(s2))
      1 - (0.001 x 0.001) = 99.9999%

  real_world:
    aws_s3: "99.999999999% durability (eleven 9s), 99.99% availability"
    google_search: "99.999% availability target"
    stripe_api: "99.999% uptime SLA"
```

## Consistency Models
```
consistency:
  definition: |
    Determines what data a read operation returns after a write.
    Stronger consistency = more correct but slower.
    Weaker consistency = faster but may return stale data.

  strong_consistency:
    description: |
      Every read receives the most recent write. All nodes see the
      same data at the same time.
    how: All writes must be confirmed by all (or quorum) replicas before ack
    pros:
      - No stale reads, simplest mental model
    cons:
      - Higher latency, lower availability
    examples: "Bank account balances, inventory counts, seat booking"

  eventual_consistency:
    description: |
      Reads may return stale data, but given enough time with no new
      writes, all replicas converge to the same value.
    how: Writes propagate asynchronously to replicas
    pros:
      - Low latency, high availability
    cons:
      - May return stale data, harder to reason about
    convergence_time: "Usually milliseconds to seconds"
    examples: "Social media likes, DNS propagation, shopping cart"

  causal_consistency:
    description: |
      Operations that are causally related are seen in the same order
      by all nodes. Concurrent (unrelated) operations can be seen in
      any order.
    example: "If user A posts, then user B replies, everyone sees post before reply"

  read_your_writes:
    description: |
      A user always sees their own writes immediately, even if other
      users may see stale data temporarily.
    how: Route reads to the same replica that handled the write, or use session tokens
    example: "After updating profile picture, user sees new picture even if CDN cache is stale"
```

## CAP Theorem
```
cap_theorem:
  definition: |
    In a distributed system, you can only guarantee TWO of three properties
    simultaneously: Consistency, Availability, Partition Tolerance.
    Since network partitions are unavoidable, the real choice is C vs A during a partition.

  properties:
    consistency: Every read receives the most recent write or an error
    availability: Every request receives a non-error response (may be stale)
    partition_tolerance: System continues operating despite network partitions between nodes

  diagram: |
            Consistency (C)
               /\
              /  \
             /    \
            / CP   \
           / systems\
          /----------\
         / CA systems \
        / (only if no  \
       /  partitions)   \
      /                  \
     /     AP systems     \
    /______________________\
  Availability (A) ---- Partition Tolerance (P)

  real_choices:
    CP_systems:
      choose: Consistency + Partition Tolerance
      sacrifice: Availability (return error rather than stale data)
      examples:
        - "MongoDB (with majority write concern)"
        - "HBase"
        - "Redis (single master)"
        - "Zookeeper"
      use_when: "Correctness is critical (bank transfers, inventory)"

    AP_systems:
      choose: Availability + Partition Tolerance
      sacrifice: Consistency (may return stale data)
      examples:
        - "Cassandra"
        - "DynamoDB"
        - "CouchDB"
        - "DNS"
      use_when: "Availability is critical (shopping cart, social feeds)"

    CA_systems:
      note: |
        Not practical in distributed systems because network partitions
        always happen. CA only works on a single node (traditional RDBMS).
      examples:"Single-node PostgreSQL, single-node MySQL"

  important_nuance: |
    CAP is about behavior DURING a partition. When the network is healthy,
    you can have all three. Systems often let you tune consistency per-operation.
```

## PACELC Theorem
```
pacelc:
  definition: |
    Extension of CAP. If there is a Partition (P), choose between
    Availability (A) and Consistency (C). Else (E), when running normally,
    choose between Latency (L) and Consistency (C).

  formula: "If P then A|C, Else L|C"

  why_it_matters: |
    CAP only describes behavior during partitions. PACELC also captures
    the latency-consistency tradeoff during normal operation. Most of
    the time the network is fine, so the E/L/C choice matters more in practice.

  examples:
    DynamoDB: "PA/EL - choose availability during partition, low latency normally"
    Cassandra: "PA/EL - same as DynamoDB"
    MongoDB: "PC/EC - choose consistency always"
    MySQL_with_sync_replication: "PC/EC - consistency at the cost of latency"
    PNUTS_Yahoo: "PC/EL - consistent during partition, low latency normally"

  diagram: |
    Network Status:
    +------------------+      +------------------+
    | PARTITION exists  |      | NO PARTITION     |
    |                   |      |                  |
    | Choose:           |      | Choose:          |
    | A (Availability)  |      | L (Latency)      |
    |    or             |      |    or            |
    | C (Consistency)   |      | C (Consistency)  |
    +------------------+      +------------------+
```

## Throughput vs Latency
```
throughput_vs_latency:
  throughput:
    definition: Number of operations completed per unit of time
    units: "requests/second (RPS), queries/second (QPS), MB/s, transactions/sec"
    analogy: "Number of cars passing through a highway per hour"

  latency:
    definition: Time taken for a single operation from start to finish
    units: "milliseconds (ms), measured as p50, p95, p99 percentiles"
    analogy: "Time for one car to travel from point A to point B"

  relationship: |
    They are related but NOT inversely proportional always.
    - Adding more lanes (parallelism) increases throughput without affecting latency
    - A system can have high throughput AND high latency (batch processing)
    - A system can have low throughput AND low latency (single fast query)

  percentiles:
    p50: "Median - 50% of requests are faster than this"
    p95: "95% of requests are faster, 5% are slower"
    p99: "99% of requests are faster, 1% are slower (tail latency)"
    why_p99_matters: |
      The slowest 1% of requests often belong to your most active users
      (more data, more features, bigger accounts). Optimizing tail latency
      improves experience for your best customers.

  diagram: |
    Latency Distribution:
    Requests
    |
    |  *
    | ***
    | *****
    | *******
    | *********
    | ***********
    | **************
    | *******************
    | *****************************............
    +--+----+----+----+----+----+----+-----> ms
       10   50  100  200  500  1000 2000
           p50       p95  p99
```

## SLAs, SLOs, and SLIs
```
sla_slo_sli:
  SLI:
    full_name: Service Level Indicator
    definition: A quantitative measurement of a service attribute
    examples:
      - "Request latency (p99 < 200ms)"
      - "Error rate (% of 5xx responses)"
      - "Throughput (requests per second)"
      - "Availability (% of successful requests)"

  SLO:
    full_name: Service Level Objective
    definition: A target value or range for an SLI (internal goal)
    examples:
      - "99.9% of requests complete in < 200ms"
      - "Error rate < 0.1% over a rolling 30-day window"
      - "99.95% availability per month"
    note: "SLOs should be stricter than SLAs to provide a buffer"

  SLA:
    full_name: Service Level Agreement
    definition: A contract with customers specifying service guarantees and penalties
    examples:
      - "99.9% uptime, or customer receives 10% credit"
      - "AWS S3 SLA: 99.9% availability, credits if breached"
    note: "SLAs are business agreements. SLOs are engineering targets. SLIs are the actual measurements."

  relationship: |
    SLI (what you measure) --> SLO (what you target) --> SLA (what you promise)

    Example:
      SLI: Actual uptime this month = 99.95%
      SLO: Internal target = 99.95% uptime
      SLA: Customer contract = 99.9% uptime (with penalty)
      Status: SLI meets SLO, SLO exceeds SLA. All good.
```

## Back-of-Envelope Estimation
```
estimation:
  purpose: |
    Quickly estimate system capacity requirements during design.
    Not about exact numbers but about order of magnitude and feasibility.

  key_numbers_to_memorize:
    powers_of_two:
      - "2^10 = 1 Thousand (1 KB)"
      - "2^20 = 1 Million (1 MB)"
      - "2^30 = 1 Billion (1 GB)"
      - "2^40 = 1 Trillion (1 TB)"
      - "2^50 = 1 Quadrillion (1 PB)"

    latency_numbers:
      L1_cache_ref: "0.5 ns"
      L2_cache_ref: "7 ns"
      RAM_ref: "100 ns"
      SSD_random_read: "150 us (150,000 ns)"
      HDD_seek: "10 ms (10,000,000 ns)"
      same_datacenter_roundtrip: "0.5 ms"
      cross_continent_roundtrip: "150 ms"

    throughput_estimates:
      sequential_read_SSD: "1 GB/s"
      sequential_read_HDD: "100 MB/s"
      network_within_datacenter: "10 Gbps"
      single_server_QPS: "10K-50K simple requests/sec"

  common_calculations:
    QPS:
      formula: "Daily Active Users x Avg requests per user / 86400 seconds"
      example: |
        100M DAU x 10 requests/day = 1B requests/day
        1B / 86400 = ~11,600 QPS
        Peak QPS = 2x to 5x average = ~50,000 QPS

    storage:
      formula: "Number of objects x Size per object x Retention period"
      example: |
        Twitter: 500M tweets/day x 280 bytes avg = 140 GB/day
        Per year: 140 GB x 365 = ~50 TB/year
        5 years with replication (3x): 50 x 5 x 3 = 750 TB

    bandwidth:
      formula: "QPS x Average response size"
      example: |
        50,000 QPS x 10 KB avg response = 500 MB/s = 4 Gbps

    number_of_servers:
      formula: "Peak QPS / QPS per server"
      example: |
        50,000 peak QPS / 10,000 QPS per server = 5 servers
        With redundancy (2x): 10 servers
```

## Capacity Planning
```
capacity_planning:
  definition: |
    Estimating future resource requirements (compute, storage, network)
    based on growth projections to ensure the system can handle the load.

  steps:
    1_measure_current: "Establish baselines for CPU, memory, disk, network, QPS"
    2_project_growth: "Estimate user growth rate (e.g., 2x per year)"
    3_identify_bottlenecks: "Which resource hits limit first?"
    4_plan_ahead: "Provision for 3-6 months ahead, not just today"
    5_build_headroom: "Keep utilization below 70% for burst capacity"

  example: |
    Current: 10K QPS, 60% CPU utilization on 5 servers
    Growth: 2x users expected in 12 months
    Projection: 20K QPS will need ~10 servers
    Plan: Scale to 12 servers (20% headroom) by month 10

  common_bottlenecks:
    - CPU (compute-heavy workloads)
    - Memory (caching, in-memory processing)
    - Disk I/O (database-heavy workloads)
    - Network bandwidth (media-heavy, data transfer)
    - Database connections (connection pool exhaustion)
```

## Redundancy and Replication
```
redundancy:
  definition: |
    Duplication of critical components to eliminate single points of failure.
    If one component fails, the backup takes over.

  types:
    active_passive:
      also_called: Primary-secondary, hot standby
      how: "Primary handles traffic, secondary is on standby and takes over on failure"
      failover_time: "Seconds to minutes"
      example: "Database with a standby replica"

    active_active:
      how: "All nodes handle traffic simultaneously, if one fails, others absorb its load"
      failover_time: "Near-instant (traffic just goes to remaining nodes)"
      example: "Multiple web servers behind a load balancer"

  replication:
    definition: Keeping copies of data on multiple nodes
    synchronous:
      how: "Write is acknowledged only after ALL replicas confirm"
      pros: "Strong consistency, no data loss on failover"
      cons: "Higher write latency, reduced availability if replica is down"
    asynchronous:
      how: "Write is acknowledged after primary confirms, replicas updated later"
      pros: "Low write latency, high availability"
      cons: "Possible data loss on primary failure (replication lag)"
    semi_synchronous:
      how: "Write acknowledged after primary + at least one replica confirms"
      pros: "Balance of consistency and performance"

  database_replication:
    master_slave:
      also_called: Primary-replica
      how: |
        One master handles all writes.
        Multiple slaves replicate from master and handle reads.
      pros:
        - Simple to set up
        - Scales reads horizontally
        - Slaves can serve as backup
      cons:
        - Single point of failure for writes (until failover)
        - Replication lag on slaves
      diagram: |
        Writes --> [Master DB]
                     |  async replication
                     +---> [Slave 1] <-- Reads
                     +---> [Slave 2] <-- Reads
                     +---> [Slave 3] <-- Reads

    master_master:
      also_called: Multi-master, active-active replication
      how: |
        Multiple masters accept writes. Each replicates to the others.
      pros:
        - No single point of failure for writes
        - Can write to nearest node (lower latency)
      cons:
        - Write conflicts (two masters update same row simultaneously)
        - Conflict resolution is complex
        - Higher complexity overall
      conflict_resolution:
        - "Last-write-wins (timestamp based)"
        - "Application-level resolution"
        - "CRDTs (conflict-free replicated data types)"
```

## Sharding and Partitioning
```
sharding:
  definition: |
    Splitting data across multiple databases/nodes so each holds
    a subset. Each subset is called a shard (or partition).
    Different from replication: replication copies ALL data to every node,
    sharding splits data so each node holds DIFFERENT data.

  why_shard:
    - "Single DB cannot hold all data (storage limit)"
    - "Single DB cannot handle all queries (throughput limit)"
    - "Reduce query latency (smaller dataset per shard)"

  strategies:
    hash_based:
      how: "shard_id = hash(partition_key) % num_shards"
      pros:
        - Even data distribution
        - Simple to implement
      cons:
        - Adding/removing shards reshuffles most data (modulo changes)
        - Range queries across shards are expensive
      example: "shard = hash(user_id) % 4"

    range_based:
      how: "Assign contiguous ranges of the partition key to each shard"
      pros:
        - Range queries on partition key are efficient
        - Easy to understand
      cons:
        - Hot spots if data is not evenly distributed
        - One shard may get much more traffic than others
      example: |
        Shard A: user_id 1 - 1,000,000
        Shard B: user_id 1,000,001 - 2,000,000
        Shard C: user_id 2,000,001 - 3,000,000

    directory_based:
      how: "A lookup service maps each key to its shard"
      pros:
        - Flexible, can move data between shards easily
      cons:
        - Lookup service is a single point of failure
        - Extra hop for every query
      example: "A metadata table: {user_id_range -> shard_address}"

  choosing_partition_key:
    goals:
      - "Even data distribution across shards"
      - "Queries can be routed to a single shard (avoid scatter-gather)"
      - "Related data is co-located (e.g., user's posts on same shard as user)"
    bad_keys: "Auto-increment ID with range sharding (all new data goes to last shard)"
    good_keys: "user_id for user-centric apps, tenant_id for multi-tenant SaaS"

  problems:
    joins_across_shards: "Cannot do SQL joins across shards easily, denormalize or use application-level joins"
    rebalancing: "Adding a shard requires moving data; consistent hashing minimizes this"
    hot_shards: "Celebrity problem - one key has disproportionate traffic"
```

## Consistent Hashing Deep Dive
```
consistent_hashing:
  definition: |
    A hashing technique where adding or removing a node only requires
    remapping K/N keys on average (K = total keys, N = total nodes),
    instead of remapping almost all keys as with modulo hashing.

  problem_with_modulo_hashing: |
    server = hash(key) % N
    If N changes (add/remove server), almost ALL keys remap.
    Example: 3 servers -> 4 servers, ~75% of keys move.

  how_it_works:
    step_1: "Hash both servers and keys onto a circular ring (0 to 2^32 - 1)"
    step_2: "To find which server owns a key, walk clockwise from the key's position"
    step_3: "First server encountered clockwise owns that key"
    step_4: "Adding a server only affects keys between it and its predecessor"
    step_5: "Removing a server only moves its keys to the next server clockwise"

  diagram: |
    Hash Ring (0 to 2^32):

              Key2
               |
        S_A ---+--- S_B
       /                \
      |                  |
      |    Hash Ring     |
      |                  |
       \                /
        S_D ---+--- S_C
               |
              Key1

    Key1 -> walk clockwise -> owned by S_C
    Key2 -> walk clockwise -> owned by S_B

    Add S_E between S_A and S_B:
    Only keys between S_A and S_E move from S_B to S_E.
    All other keys stay put.

  virtual_nodes:
    problem: |
      With few servers, distribution is uneven. One server may own
      a huge arc of the ring while another owns a tiny arc.
    solution: |
      Each physical server maps to multiple virtual nodes on the ring.
      e.g., Server A -> vnode_A1, vnode_A2, vnode_A3, ... vnode_A150
    benefit:
      - Much more even distribution
      - Powerful servers get more virtual nodes
      - When a server is removed, its load spreads evenly to many servers
    typical_count: "100-200 virtual nodes per physical server"

  real_world_usage:
    - "Amazon DynamoDB (partition assignment)"
    - "Apache Cassandra (token ring)"
    - "Akamai CDN (content routing)"
    - "Discord (guild/server distribution)"
    - "Memcached clients (key distribution)"
```

## Caching Layers
```
caching_layers:
  overview: |
    Caching stores frequently accessed data closer to the consumer.
    Multiple layers of caching reduce load progressively.

  layers:
    client_cache:
      where: "Browser, mobile app"
      what: "HTML, CSS, JS, images, API responses"
      how: "HTTP cache headers (Cache-Control, ETag, Last-Modified)"
      ttl: "Minutes to days"

    CDN_cache:
      where: "Edge servers close to users (CloudFront, Cloudflare, Akamai)"
      what: "Static assets, cacheable API responses"
      how: "CDN pulls from origin, caches at edge, serves subsequent requests"
      benefit: "Reduces latency by serving from geographically closer server"

    application_cache:
      where: "Application server memory or distributed cache (Redis, Memcached)"
      what: "Database query results, computed values, session data"
      how: "Cache-aside, read-through, write-through patterns"
      ttl: "Seconds to hours"

    database_cache:
      where: "Database engine internals"
      what: "Query result cache, buffer pool (pages in memory)"
      how: "Automatic in most databases, configurable buffer pool size"
      note: "InnoDB buffer pool, PostgreSQL shared_buffers"

  diagram: |
    User Request Flow:
    [Client] --1--> [CDN] --2--> [Load Balancer] --3--> [App Server]
                                                              |
                                                         [App Cache / Redis]
                                                              |
                                                         [Database]

    Each layer acts as a shield for the next:
    Layer 1 hit = 1ms    (client cache)
    Layer 2 hit = 10ms   (CDN)
    Layer 3 hit = 5ms    (app cache / Redis)
    Layer 4 hit = 50ms   (database cache / buffer pool)
    Full miss   = 200ms+ (disk read)
```

## CDN (Content Delivery Network)
```
cdn:
  definition: |
    A geographically distributed network of servers that caches
    and serves content from locations close to the end user,
    reducing latency and load on the origin server.

  how_it_works:
    step_1: "User requests resource (e.g., image)"
    step_2: "DNS resolves to nearest CDN edge server"
    step_3: "If edge has cached copy (hit) -> serve immediately"
    step_4: "If edge does not have it (miss) -> fetch from origin, cache, serve"

  push_vs_pull:
    push_CDN:
      how: "You upload content to CDN proactively"
      pros: "Content available immediately, you control what's cached"
      cons: "You manage uploads, may waste space on unpopular content"
      best_for: "Known static assets (CSS, JS bundles, videos)"
    pull_CDN:
      how: "CDN fetches from origin on first request, then caches"
      pros: "No upload management, only caches what's actually requested"
      cons: "First request is slow (origin fetch)"
      best_for: "Dynamic/unpredictable content patterns"

  cache_invalidation:
    - "TTL expiry (Cache-Control: max-age=3600)"
    - "Purge API (manually invalidate specific URLs)"
    - "Versioned URLs (app-v2.1.js changes filename on deploy)"

  real_world:
    cloudflare: "Reverse proxy CDN, DDoS protection, edge compute"
    cloudfront: "AWS CDN, integrates with S3/EC2/Lambda@Edge"
    akamai: "Largest CDN, powers ~30% of web traffic"
```

## Message Queues
```
message_queues:
  definition: |
    An intermediary that holds messages between producers and consumers,
    enabling asynchronous communication and decoupling components.

  benefits:
    - "Decoupling: producer doesn't need to know about consumer"
    - "Buffering: absorbs traffic spikes"
    - "Reliability: messages persist until consumed"
    - "Async processing: producer doesn't wait for consumer"

  delivery_semantics:
    at_most_once: "Message delivered 0 or 1 times. May lose messages."
    at_least_once: "Message delivered 1+ times. May duplicate. Consumer must be idempotent."
    exactly_once: "Message delivered exactly 1 time. Hard to achieve. Kafka supports with transactions."

  when_to_use:
    - "Background tasks (email sending, image processing)"
    - "Smoothing traffic spikes (order processing)"
    - "Decoupling microservices"
    - "Event-driven architectures"
    - "Retry with backoff for failed operations"

  diagram: |
    [Producer A] --\
                    \
    [Producer B] ----> [Message Queue] ----> [Consumer 1]
                    /       |
    [Producer C] --/        +-------------> [Consumer 2]

    Messages sit in queue until consumed.
    If consumer is down, messages wait.
    Multiple consumers can process in parallel.

  real_world:
    kafka: "High-throughput event streaming, log-based, partition-ordered"
    rabbitmq: "Traditional message broker, AMQP, complex routing"
    sqs: "AWS managed queue, simple, scales automatically"
```

## Load Balancers
```
load_balancers:
  definition: |
    Distributes incoming requests across multiple backend servers
    to ensure no single server is overwhelmed.

  layers:
    L4_load_balancer:
      operates_at: "Transport layer (TCP/UDP)"
      how: "Routes based on IP and port, does not inspect content"
      pros: "Fast, low overhead"
      cons: "Cannot make routing decisions based on URL/headers"
      example: "AWS NLB, HAProxy in TCP mode"

    L7_load_balancer:
      operates_at: "Application layer (HTTP/HTTPS)"
      how: "Inspects HTTP headers, URL, cookies to make routing decisions"
      pros: "Content-based routing, SSL termination, caching"
      cons: "Higher overhead than L4"
      example: "AWS ALB, Nginx, HAProxy in HTTP mode"

  algorithms:
    round_robin: "Distribute sequentially: A, B, C, A, B, C..."
    weighted_round_robin: "More traffic to beefier servers"
    least_connections: "Send to server with fewest active connections"
    ip_hash: "Same client IP always goes to same server"
    consistent_hashing: "Minimal remapping when servers added/removed"
    random: "Pick a server randomly (surprisingly effective)"

  health_checks:
    how: "Periodically send requests (HTTP GET /health) to each server"
    on_failure: "Remove unhealthy server from rotation"
    on_recovery: "Re-add server to rotation after consecutive successes"

  diagram: |
    Internet
       |
    [Load Balancer]
       |
    +--+--+--+
    |  |  |  |
    S1 S2 S3 S4   (backend servers)
```

## Reverse Proxy
```
reverse_proxy:
  definition: |
    A server that sits in front of backend servers, forwarding
    client requests to the appropriate backend and returning the response.
    The client only sees the proxy, not the backend servers.

  difference_from_load_balancer: |
    A load balancer IS a reverse proxy, but a reverse proxy can do more:
    - SSL termination
    - Caching
    - Compression
    - Rate limiting
    - Request/response transformation
    A reverse proxy with one backend is still useful.

  benefits:
    - "Security: hides backend server IPs and topology"
    - "SSL termination: handles HTTPS, backends use plain HTTP"
    - "Caching: cache static content, reduce backend load"
    - "Compression: gzip/brotli responses"
    - "Load balancing: distribute across backends"

  examples: "Nginx, HAProxy, Envoy, Traefik, Caddy"

  diagram: |
    Client --> [Reverse Proxy (Nginx)] --> [App Server 1]
                                       --> [App Server 2]
                                       --> [App Server 3]

    Client sees: api.example.com (proxy IP)
    Client does NOT see: 10.0.1.5:8080, 10.0.1.6:8080 (backend IPs)
```

## API Gateway
```
api_gateway:
  definition: |
    A single entry point for all client requests in a microservices
    architecture. It routes, composes, and transforms requests.

  responsibilities:
    - "Request routing (route /users to user-service, /orders to order-service)"
    - "Authentication and authorization"
    - "Rate limiting and throttling"
    - "Request/response transformation"
    - "API composition (aggregate multiple service calls into one response)"
    - "Caching"
    - "Logging and monitoring"
    - "SSL termination"
    - "Protocol translation (REST to gRPC)"

  diagram: |
    Mobile App --\
                  \
    Web App -------> [API Gateway] ---> [User Service]
                  /       |         --> [Order Service]
    3rd Party ---/        |         --> [Payment Service]
                          |         --> [Notification Service]
                          |
                    [Rate Limiting]
                    [Auth/JWT Validation]
                    [Logging]

  examples:
    kong: "Open source, Lua/Nginx based, plugin ecosystem"
    aws_api_gateway: "Managed, integrates with Lambda"
    envoy: "High-performance proxy, used in service meshes"
    zuul: "Netflix gateway, Java-based"
```

## Rate Limiting
```
rate_limiting:
  definition: |
    Controlling the number of requests a client can make in a given
    time window. Protects against abuse, DDoS, and ensures fair usage.

  algorithms:
    token_bucket:
      how: |
        1. Bucket holds tokens (max = bucket size)
        2. Tokens added at fixed rate (e.g., 10/sec)
        3. Each request consumes one token
        4. If no tokens, request is rejected (HTTP 429)
      pros: "Allows short bursts, simple"
      cons: "Burst size limited by bucket capacity"

    sliding_window_log:
      how: |
        1. Keep timestamp of every request in a sorted set
        2. On new request, remove entries older than window
        3. If count < limit, allow; else reject
      pros: "Precise, no boundary issues"
      cons: "Memory intensive (store every timestamp)"

    sliding_window_counter:
      how: |
        1. Combine current and previous window counts
        2. Weight previous window by overlap percentage
        3. If weighted count < limit, allow
      pros: "Memory efficient, smooth, no boundary spikes"
      cons: "Approximate (but close enough)"

    fixed_window:
      how: "Count requests in fixed time windows (e.g., per minute)"
      pros: "Simple, memory efficient"
      cons: "Burst at window boundary (2x rate possible)"

  distributed_rate_limiting:
    challenge: "Multiple server instances need shared state"
    solution: "Use Redis with atomic INCR and EXPIRE"
    implementation: |
      key = "rate_limit:{user_id}:{window}"
      count = INCR(key)
      if count == 1: EXPIRE(key, window_seconds)
      if count > limit: reject with 429
```

## Idempotency
```
idempotency:
  definition: |
    An operation is idempotent if performing it multiple times has the
    same effect as performing it once. Critical for reliability in
    distributed systems where retries are common.

  why_it_matters: |
    Networks are unreliable. A client may retry a request because:
    - Timeout (server processed it but response was lost)
    - Load balancer retried on a different server
    - Message queue redelivered a message
    Without idempotency, retries cause duplicate charges, double posts, etc.

  idempotent_http_methods:
    GET: "Yes - reading data doesn't change state"
    PUT: "Yes - setting a value to X is the same whether done 1 or 5 times"
    DELETE: "Yes - deleting an already-deleted resource is a no-op"
    POST: "NO - creating a resource twice creates two resources"

  making_POST_idempotent:
    idempotency_key:
      how: |
        1. Client generates a unique key (UUID) per intended operation
        2. Client sends key in header: Idempotency-Key: <uuid>
        3. Server checks if key was already processed
        4. If yes, return cached response
        5. If no, process and store result with the key
      used_by: "Stripe, PayPal, Square for payment APIs"

  example: |
    POST /payments
    Idempotency-Key: abc-123
    {amount: 100, currency: "USD"}

    First call: Process payment, store result with key abc-123
    Retry call: Key abc-123 exists, return stored result (no double charge)
```

## Circuit Breaker Pattern
```
circuit_breaker:
  definition: |
    A pattern that prevents cascading failures by stopping requests
    to a failing service. Like an electrical circuit breaker that trips
    to prevent damage when current is too high.

  states:
    closed:
      description: "Normal operation, requests flow through"
      behavior: "Track failures. If failure count exceeds threshold, trip to OPEN"
    open:
      description: "Service is considered down, requests fail fast"
      behavior: "Return error immediately without calling the service. After timeout, move to HALF-OPEN"
    half_open:
      description: "Testing if service has recovered"
      behavior: "Allow limited requests through. If they succeed, move to CLOSED. If they fail, back to OPEN"

  diagram: |
    +--------+   failure threshold   +------+   timeout   +-----------+
    | CLOSED | ---- exceeded ------> | OPEN | --------->  | HALF-OPEN |
    +--------+                       +------+             +-----------+
        ^                               ^                      |
        |                               |                      |
        +--- success in half-open ------+---- failure ---------+

  parameters:
    failure_threshold: "Number of failures before tripping (e.g., 5)"
    timeout: "How long to wait before trying again (e.g., 30 seconds)"
    half_open_max_requests: "Number of test requests in half-open state (e.g., 3)"

  real_world:
    netflix_hystrix: "Original circuit breaker library (now in maintenance)"
    resilience4j: "Modern Java circuit breaker library"
    polly: ".NET resilience library"
    envoy: "Service mesh with built-in circuit breaking"
```

## Bulkhead Pattern
```
bulkhead:
  definition: |
    Isolate components so that failure in one does not cascade to others.
    Named after ship bulkheads - watertight compartments that prevent
    a single hull breach from sinking the entire ship.

  types:
    thread_pool_isolation:
      how: |
        Each downstream service gets its own thread pool.
        If Service A's pool is exhausted, Service B's pool is unaffected.
      example: |
        Thread pool for Payment Service: 20 threads
        Thread pool for Email Service: 10 threads
        If email service hangs, only its 10 threads are blocked.
        Payment service continues working fine.

    connection_pool_isolation:
      how: "Separate database connection pools per service or per use case"

    process_isolation:
      how: "Run components in separate processes or containers"

  diagram: |
    Without Bulkhead:                With Bulkhead:
    +------------------+             +--------+ +--------+
    | Shared Pool      |             | Pool A | | Pool B |
    | [all threads]    |             | [10]   | | [10]   |
    | If one service   |             +--------+ +--------+
    | hangs, all       |             Service A   Service B
    | threads blocked  |             failure     unaffected
    +------------------+

  real_world: |
    Kubernetes resource limits act as bulkheads:
    each pod gets CPU/memory limits, one pod cannot starve others.
```

## Leader Election
```
leader_election:
  definition: |
    A process by which distributed nodes choose one node to act as
    the leader/coordinator. The leader handles writes, assigns tasks,
    or coordinates other nodes.

  why_needed:
    - "Only one node should write to avoid conflicts"
    - "Task assignment needs a coordinator"
    - "Cluster management decisions (rebalancing, failover)"

  approaches:
    bully_algorithm:
      how: |
        1. Node detects leader is down
        2. Sends election message to all higher-ID nodes
        3. If no higher-ID node responds, it becomes leader
        4. If a higher-ID node responds, it takes over the election
      pros: "Simple"
      cons: "Relies on node IDs, chatty"

    raft_leader_election:
      how: |
        1. All nodes start as followers with random election timeouts
        2. If a follower's timeout expires without hearing from leader,
           it becomes a candidate and requests votes
        3. Candidate wins if it gets majority votes
        4. Leader sends periodic heartbeats to maintain authority
      pros: "Well-understood, widely used, handles network partitions"

    using_external_service:
      how: "Use Zookeeper, etcd, or Consul for leader election"
      mechanism: "Ephemeral lock/lease. Leader holds the lock. If leader dies, lock expires, new election."
      pros: "Battle-tested, handles edge cases"
      cons: "Dependency on external service"

  real_world:
    kafka: "Uses Zookeeper (or KRaft) for controller election"
    elasticsearch: "Master node election using Zen discovery"
    redis_sentinel: "Sentinels elect among themselves, then promote a new master"
```

## Consensus Algorithms
```
consensus:
  definition: |
    Algorithms that allow distributed nodes to agree on a single value
    or sequence of operations, even when some nodes fail.
    The foundation of reliable distributed systems.

  raft_basics:
    overview: |
      Raft is designed for understandability. It decomposes consensus
      into leader election, log replication, and safety.
    roles:
      leader: "Handles all client requests, replicates log to followers"
      follower: "Passive, responds to leader's requests"
      candidate: "Temporarily, during leader election"
    log_replication: |
      1. Client sends command to leader
      2. Leader appends to its log
      3. Leader replicates entry to followers
      4. Once majority confirm, entry is committed
      5. Leader applies command and responds to client
    safety: "A node can only become leader if its log is at least as up-to-date as majority"

  paxos_basics:
    overview: |
      Original consensus algorithm by Leslie Lamport.
      Harder to understand than Raft but mathematically proven correct.
    phases:
      prepare: "Proposer sends prepare(n) to acceptors with proposal number n"
      promise: "Acceptors promise not to accept proposals with number < n"
      accept: "Proposer sends accept(n, value), acceptors accept if promise still valid"
      learn: "Once majority accept, value is chosen, learners are notified"
    note: "Multi-Paxos optimizes by using a stable leader, similar to Raft"

  real_world:
    etcd: "Raft-based distributed key-value store (used by Kubernetes)"
    zookeeper: "ZAB protocol (Zookeeper Atomic Broadcast), similar to Paxos"
    cockroachdb: "Raft for consensus on range replicas"
    google_spanner: "Paxos for global consensus"
```

## Distributed Locking
```
distributed_locking:
  definition: |
    A mechanism to ensure that only one process across multiple nodes
    can access a shared resource at a time.

  why_needed:
    - "Prevent double-spending in payment systems"
    - "Ensure only one worker processes a job"
    - "Coordinate access to shared files or resources"

  redis_based_lock:
    simple_lock:
      acquire: "SET lock_key unique_value NX EX 30"
      release: |
        Only release if you own it (Lua script for atomicity):
        if redis.call('get', KEYS[1]) == ARGV[1] then
          return redis.call('del', KEYS[1])
        end
      problems:
        - "Single Redis instance is a SPOF"
        - "Lock can expire before work is done (clock drift)"

    redlock:
      how: |
        1. Acquire lock on N/2+1 (majority) of N independent Redis instances
        2. Use same key and unique value on all instances
        3. If majority acquired within validity time, lock is held
        4. To release, send unlock to ALL instances
      controversy: |
        Martin Kleppmann argues Redlock is unsafe due to clock drift
        and GC pauses. Use fencing tokens for correctness.

  zookeeper_based_lock:
    how: |
      1. Create ephemeral sequential node under /locks/resource
      2. If your node has the lowest sequence number, you hold the lock
      3. Otherwise, watch the node with the next-lower sequence number
      4. When it's deleted, check again
    pros: "Ephemeral nodes auto-delete if client dies (no stuck locks)"

  fencing_token:
    problem: "Client A holds lock, GC pause, lock expires, Client B gets lock, Client A resumes and writes"
    solution: |
      Each lock acquisition gets a monotonically increasing token.
      Resource rejects operations with an older token than the last seen.
```

## Bloom Filters
```
bloom_filter:
  definition: |
    A space-efficient probabilistic data structure that tests whether
    an element is a member of a set. It can tell you:
    - "Definitely NOT in the set" (100% accurate)
    - "PROBABLY in the set" (may have false positives)
    It never produces false negatives.

  how_it_works:
    step_1: "Initialize a bit array of m bits, all set to 0"
    step_2: "Use k independent hash functions"
    step_3: |
      To ADD an element:
        Hash element with all k functions -> get k positions
        Set those k bits to 1
    step_4: |
      To CHECK an element:
        Hash element with all k functions -> get k positions
        If ALL k bits are 1 -> "probably in set"
        If ANY bit is 0 -> "definitely not in set"

  diagram: |
    Bit Array (m=10):  [0][0][0][0][0][0][0][0][0][0]

    Add "hello" (h1=2, h2=5, h3=8):
                       [0][0][1][0][0][1][0][0][1][0]

    Add "world" (h1=1, h2=5, h3=9):
                       [0][1][1][0][0][1][0][0][1][1]

    Check "hello": bits 2,5,8 all = 1 -> "probably yes"
    Check "foo":   bits 3,6,7 -> bit 3 = 0 -> "definitely no"

  properties:
    false_positive_rate: "Depends on m (bits), n (elements), k (hash functions)"
    optimal_k: "k = (m/n) * ln(2)"
    no_deletion: "Cannot remove elements (use Counting Bloom Filter for that)"
    space_efficiency: "~10 bits per element for 1% false positive rate"

  real_world:
    chrome: "Safe browsing checks URLs against a bloom filter before full lookup"
    cassandra: "Checks if a row exists in an SSTable before doing disk I/O"
    medium: "Avoids recommending articles a user has already read"
    akamai: "Detects one-hit-wonders to avoid caching rarely accessed content"
```

## Trade-offs Summary
```
tradeoffs:
  key_tensions:
    consistency_vs_availability: "CAP theorem - during partition, pick one"
    latency_vs_consistency: "Strong consistency requires coordination = more latency"
    latency_vs_durability: "Sync writes to disk are slow but safe"
    throughput_vs_latency: "Batching increases throughput but adds latency"
    simplicity_vs_scalability: "Distributed systems scale but are complex"
    cost_vs_reliability: "More redundancy = more servers = more cost"
    read_vs_write_performance: "Denormalization speeds reads but slows writes"
    freshness_vs_performance: "Caching speeds access but data may be stale"

  no_silver_bullet: |
    Every system design decision involves trade-offs.
    The job of a system designer is to understand the requirements
    and make the right trade-offs for the specific use case.
    There is no universally "best" architecture.
```
