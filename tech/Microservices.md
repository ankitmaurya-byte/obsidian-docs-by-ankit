# Microservices

## What are Microservices
```
overview:
  definition: |
    Microservices is an architectural style where an application is
    composed of small, independent services that communicate over
    well-defined APIs. Each service owns its data and business logic.
  key_properties:
    - Each service is independently deployable
    - Each service owns its own data/database
    - Services communicate via network (HTTP, gRPC, messaging)
    - Small team can own and maintain a service
    - Each service can use different tech stack
  contrast: |
    Monolith: one codebase, one deployment, one database
    Microservices: many codebases, independent deployments, many databases
```

## Microservices vs Monolith
```
comparison:

  monolith:
    structure: Single codebase, single deployment unit
    database: Shared database
    scaling: Scale entire application
    deployment: Deploy everything together
    communication: Function calls (in-process)
    complexity: Simple at first, complex as it grows
    team_size: Works well for small teams (< 10 devs)
    debugging: Easy (single process, single log)
    data_consistency: ACID transactions
    best_for:
      - Early-stage startups / MVPs
      - Small teams
      - Simple domain
      - When speed of initial development matters most

  microservices:
    structure: Multiple codebases, independent services
    database: Database per service
    scaling: Scale individual services independently
    deployment: Deploy services independently
    communication: Network calls (HTTP, gRPC, messaging)
    complexity: Complex from the start (networking, distributed systems)
    team_size: Works well for large teams (10+ devs, multiple teams)
    debugging: Hard (distributed tracing, correlated logs)
    data_consistency: Eventual consistency
    best_for:
      - Large organizations with multiple teams
      - Complex domains with clear boundaries
      - Need to scale parts independently
      - Need different tech stacks per service

  when_to_start_with_monolith:
    - "New project / startup - you don't know the domain boundaries yet"
    - "Small team (< 5 devs)"
    - "Simple CRUD application"
    - "Need to ship fast, iterate quickly"

  when_to_move_to_microservices:
    - "Teams stepping on each other (merge conflicts, coupled deployments)"
    - "Parts of the app need different scaling"
    - "Deployment of one feature breaks unrelated features"
    - "Team has grown beyond 10-15 devs"
    - "You understand the domain well enough to draw service boundaries"
```

## Core Principles
```
principles:

  single_responsibility:
    description: Each service does one thing well
    example: "Order service handles orders, Payment service handles payments"
    anti_pattern: "A 'user service' that also handles auth, notifications, and billing"

  loose_coupling:
    description: Services know as little as possible about each other
    how:
      - "Communicate via well-defined APIs or events"
      - "Don't share databases"
      - "Don't share code libraries (except utilities)"
    anti_pattern: "Service A directly queries Service B's database"

  high_cohesion:
    description: Related functionality grouped within one service
    example: "All payment logic (charge, refund, invoice) in Payment service"

  database_per_service:
    description: Each service owns and manages its own data store
    why:
      - "Services can evolve schemas independently"
      - "No coupling through shared tables"
      - "Can choose best DB for the job (Postgres, Mongo, Redis)"
    challenge: "Cross-service queries and data consistency"

  autonomous_teams:
    description: A team owns the full lifecycle of a service
    responsibilities: "Build, test, deploy, monitor, on-call"
    enables: "Independent velocity, no cross-team coordination for deploys"

  design_for_failure:
    description: Assume any service or network call can fail
    techniques:
      - Circuit breakers
      - Retries with backoff
      - Timeouts on every call
      - Fallback responses
      - Bulkhead pattern
```

## Service Communication
```
communication:

  synchronous:
    description: Caller waits for response (request-response)

    rest_http:
      description: JSON over HTTP, most common
      pros:
        - Simple, widely understood
        - Easy to debug (curl, browser)
        - Great tooling (OpenAPI/Swagger)
      cons:
        - Verbose (JSON, HTTP headers)
        - No streaming (without SSE/WebSocket)
        - Coupling between caller and callee
      best_for: Public APIs, CRUD operations, simple interactions

    grpc:
      description: Protocol Buffers over HTTP/2
      pros:
        - Much faster than REST (binary, smaller payload)
        - Streaming (server, client, bidirectional)
        - Strongly typed (proto definitions)
        - Code generation for multiple languages
      cons:
        - Harder to debug (binary format)
        - Need proto file management
        - Browser support limited (needs grpc-web)
      best_for: Internal service-to-service, high-throughput, streaming

  asynchronous:
    description: Caller sends message and moves on, no waiting

    message_queue:
      description: Point-to-point via queue (RabbitMQ, SQS)
      pattern: "Service A -> [Queue] -> Service B"
      pros:
        - Decoupled in time (B can be down)
        - Load leveling (queue absorbs spikes)
      best_for: Task processing, work distribution

    event_streaming:
      description: Publish events to topic (Kafka, NATS)
      pattern: "Service A publishes event -> [Topic] -> Multiple subscribers"
      pros:
        - Multiple consumers per event
        - Event replay capability
        - Event sourcing friendly
      best_for: Event-driven architectures, data pipelines

  choosing:
    need_immediate_response: "REST or gRPC (synchronous)"
    fire_and_forget: "Message queue (async)"
    one_to_many_notification: "Event streaming (async)"
    high_performance_internal: "gRPC"
    public_facing_api: "REST"
```

## Service Discovery
```
service_discovery:
  description: How services find each other's network addresses

  problem: |
    In dynamic environments (containers, K8s), service IPs
    change constantly. Hardcoding addresses doesn't work.

  patterns:
    client_side:
      description: Client queries a registry to find service instances
      how: "Client -> Service Registry -> get IP:port -> call service"
      tools:
        - "Consul (HashiCorp)"
        - "Eureka (Netflix)"
        - "etcd"
      pros: Client can load balance intelligently
      cons: Client needs discovery logic

    server_side:
      description: Load balancer handles discovery, client calls LB
      how: "Client -> Load Balancer -> routes to healthy instance"
      tools:
        - "AWS ALB/NLB"
        - "Kubernetes Service"
        - "Nginx"
      pros: Simple client, discovery logic centralized
      cons: Extra network hop

    dns_based:
      description: Use DNS to resolve service names to IPs
      how: "order-service.internal -> 10.0.1.15"
      tools:
        - "Kubernetes CoreDNS"
        - "Consul DNS"
        - "AWS Route 53 (private hosted zones)"
      pros: Universal, every language supports DNS
      cons: DNS TTL caching can serve stale IPs

    kubernetes:
      description: Built-in service discovery via Service objects
      how: |
        1. Deploy pods with labels (app=order-service)
        2. Create Service that selects those pods
        3. Other pods call: http://order-service:8080
        4. CoreDNS resolves, kube-proxy routes to healthy pod
```

## Circuit Breaker
```
circuit_breaker:
  description: |
    Prevents cascading failures by stopping calls to a failing
    service. Like an electrical circuit breaker that trips to
    prevent overload.

  problem: |
    Service B is slow/down. Service A keeps calling B, waiting
    for timeouts. A's threads fill up. Now A is also down.
    This cascades to every service that calls A.

  states:
    closed:
      description: Normal operation, requests flow through
      behavior: "Track failures. If failures exceed threshold -> Open"

    open:
      description: Circuit is tripped, requests fail immediately
      behavior: "Return error/fallback instantly (no call to failing service)"
      duration: "Stay open for a cooldown period (e.g., 30 seconds)"

    half_open:
      description: Test if service has recovered
      behavior: "Allow a few requests through"
      on_success: "Close the circuit (back to normal)"
      on_failure: "Open the circuit again"

  parameters:
    failure_threshold: "Number of failures to trip the circuit (e.g., 5)"
    success_threshold: "Successes in half-open to close circuit (e.g., 3)"
    timeout: "How long to stay open before half-open (e.g., 30s)"

  fallback_strategies:
    - "Return cached data"
    - "Return default/empty response"
    - "Call a different service (fallback endpoint)"
    - "Queue the request for retry later"

  tools:
    go: "sony/gobreaker, afex/hystrix-go"
    java: "Resilience4j, Netflix Hystrix (deprecated)"
    javascript: "opossum"
```

## Saga Pattern
```
saga_pattern:
  description: |
    Manages distributed transactions across multiple services.
    Instead of one ACID transaction, a saga is a sequence of
    local transactions with compensating actions on failure.

  problem: |
    Order requires: charge payment + reserve inventory + create shipment.
    These span 3 services. No single database transaction can cover all.

  types:
    choreography:
      description: Each service publishes events, next service reacts
      flow: |
        1. Order Service creates order -> publishes OrderCreated
        2. Payment Service listens -> charges card -> publishes PaymentCompleted
        3. Inventory Service listens -> reserves stock -> publishes StockReserved
        4. Shipping Service listens -> creates shipment -> publishes ShipmentCreated
      on_failure: |
        If Payment fails -> publishes PaymentFailed
        Order Service listens -> cancels order (compensating action)
      pros:
        - Simple, loosely coupled
        - No central coordinator
      cons:
        - Hard to track overall flow
        - Difficult to debug

    orchestration:
      description: Central orchestrator tells each service what to do
      flow: |
        1. Saga Orchestrator creates order
        2. Orchestrator -> Payment Service: "charge $50" -> success
        3. Orchestrator -> Inventory Service: "reserve item" -> success
        4. Orchestrator -> Shipping Service: "create shipment" -> success
        5. Orchestrator -> Order Service: "mark completed"
      on_failure: |
        If Inventory fails after Payment succeeded:
        Orchestrator -> Payment Service: "refund $50" (compensating action)
        Orchestrator -> Order Service: "mark failed"
      pros:
        - Clear flow, easy to understand
        - Easy to add steps
      cons:
        - Orchestrator is a single point of complexity
        - Tighter coupling to orchestrator

  compensating_actions:
    description: Undo operations to reverse completed steps on failure
    examples:
      payment_charged: "Issue refund"
      inventory_reserved: "Release reservation"
      email_sent: "Send cancellation email"
      order_created: "Mark order as cancelled"
```

## API Gateway
```
api_gateway:
  description: |
    Single entry point for all client requests. Routes requests
    to appropriate microservices and handles cross-cutting concerns.

  responsibilities:
    - Request routing (path-based to different services)
    - Authentication and authorization
    - Rate limiting
    - Request/response transformation
    - Load balancing
    - Caching
    - SSL termination
    - API versioning
    - Request aggregation (combine multiple service calls)
    - Logging and monitoring

  pattern:
    without_gateway: |
      Client -> Order Service
      Client -> User Service
      Client -> Payment Service
      (client needs to know all service addresses)
    with_gateway: |
      Client -> API Gateway -> Order Service
                            -> User Service
                            -> Payment Service
      (client knows one address)

  tools:
    kong: "Open source, plugin-based, Lua/Go plugins"
    aws_api_gateway: "Managed, integrates with Lambda, throttling"
    nginx: "Reverse proxy as API gateway"
    traefik: "Auto-discovery, Docker/K8s native"
    envoy: "Service mesh sidecar, gRPC-native"
    express_gateway: "Node.js based"

  bff_pattern:
    name: Backend for Frontend
    description: Separate API gateway per client type
    example:
      web_bff: "Aggregates data for web dashboard (large payloads OK)"
      mobile_bff: "Slimmer responses for mobile (bandwidth-sensitive)"
      third_party_bff: "Public API with rate limiting and versioning"
```

## Database per Service
```
database_per_service:
  description: Each microservice owns its private data store

  rules:
    - "Only the owning service reads/writes its database"
    - "Other services access data via the service's API"
    - "No shared tables between services"
    - "Each service can choose its own DB technology"

  example:
    user_service: PostgreSQL (relational, strong consistency)
    product_service: MongoDB (flexible schema, document model)
    search_service: Elasticsearch (full-text search)
    session_service: Redis (fast, TTL-based expiry)
    analytics_service: ClickHouse (columnar, fast aggregations)

  challenges:
    cross_service_queries:
      problem: "Need data from multiple services for one view"
      solutions:
        - "API composition: gateway calls multiple services, merges results"
        - "CQRS: maintain read-optimized views from events"
        - "Data replication via events: service caches needed data locally"

    distributed_transactions:
      problem: "Operation spans multiple databases"
      solution: "Saga pattern (no distributed ACID)"

    data_duplication:
      problem: "Same data exists in multiple services"
      solution: "Accept duplication, use events to keep in sync (eventual consistency)"
```

## Eventual Consistency
```
eventual_consistency:
  definition: |
    Given enough time without new updates, all copies of the data
    will converge to the same value. Not immediately consistent,
    but eventually consistent.

  why_in_microservices: |
    With database-per-service, you can't use ACID transactions
    across services. Changes propagate asynchronously via events.

  example: |
    1. User updates profile in User Service (instant)
    2. User Service publishes UserUpdated event
    3. Order Service receives event, updates its local copy (delay: 50ms-2s)
    4. During that window, Order Service has stale data

  strategies_to_handle:
    event_sourcing:
      description: Store events as source of truth, derive current state
      example: "OrderCreated -> ItemAdded -> ItemRemoved -> OrderPlaced"

    cqrs:
      name: Command Query Responsibility Segregation
      description: Separate write model from read model
      how: "Writes go to command service, reads from materialized view"

    idempotent_consumers:
      description: Processing same event twice produces same result
      how: "Track event IDs, skip if already processed"

    outbox_pattern:
      description: Write event and data in same DB transaction
      how: |
        1. Service writes to its table + outbox table in one transaction
        2. Background worker reads outbox, publishes to message broker
        3. Guarantees event is published if data is written
```

## 12-Factor App
```
twelve_factor:
  description: |
    Methodology for building modern, cloud-native applications.
    Originally by Heroku, widely adopted for microservices.

  factors:
    1_codebase: "One repo per service, tracked in version control"
    2_dependencies: "Explicitly declare dependencies (go.mod, package.json)"
    3_config: "Store config in environment variables, not in code"
    4_backing_services: "Treat databases, queues, caches as attached resources"
    5_build_release_run: "Strictly separate build, release, and run stages"
    6_processes: "Run as stateless processes; store state externally"
    7_port_binding: "Export service via port binding (self-contained)"
    8_concurrency: "Scale out via process model (more instances, not bigger)"
    9_disposability: "Fast startup and graceful shutdown"
    10_dev_prod_parity: "Keep dev, staging, prod as similar as possible"
    11_logs: "Treat logs as event streams (write to stdout)"
    12_admin_processes: "Run admin/management tasks as one-off processes"
```

## Example - gRPC Service Communication in Go
```go
// Proto definition (user.proto):
// syntax = "proto3";
// package user;
//
// service UserService {
//     rpc GetUser(GetUserRequest) returns (User);
// }
// message GetUserRequest { string id = 1; }
// message User { string id = 1; string name = 2; string email = 3; }

// --- Server (User Service) ---
package main

import (
    "context"
    "log"
    "net"

    pb "myapp/proto/user"
    "google.golang.org/grpc"
    "google.golang.org/grpc/health"
    healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

type userServer struct {
    pb.UnimplementedUserServiceServer
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    // Simulate DB lookup
    return &pb.User{
        Id:    req.Id,
        Name:  "Ankit",
        Email: "ankit@example.com",
    }, nil
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatal(err)
    }

    s := grpc.NewServer()
    pb.RegisterUserServiceServer(s, &userServer{})

    // Register gRPC health check (for load balancers / K8s)
    healthServer := health.NewServer()
    healthpb.RegisterHealthServer(s, healthServer)
    healthServer.SetServingStatus("user.UserService", healthpb.HealthCheckResponse_SERVING)

    log.Println("User service on :50051")
    s.Serve(lis)
}
```

## Example - Circuit Breaker in Go
```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "time"

    "github.com/sony/gobreaker/v2"
)

var cb *gobreaker.CircuitBreaker[[]byte]

func init() {
    cb = gobreaker.NewCircuitBreaker[[]byte](gobreaker.Settings{
        Name:        "payment-service",
        MaxRequests: 3,                // max requests in half-open state
        Interval:    10 * time.Second, // cyclic period for clearing counts (closed state)
        Timeout:     30 * time.Second, // how long to stay open before half-open
        ReadyToTrip: func(counts gobreaker.Counts) bool {
            // Open circuit after 5 consecutive failures
            return counts.ConsecutiveFailures >= 5
        },
        OnStateChange: func(name string, from, to gobreaker.State) {
            fmt.Printf("Circuit breaker %s: %s -> %s\n", name, from, to)
        },
    })
}

func callPaymentService(orderID string) ([]byte, error) {
    result, err := cb.Execute(func() ([]byte, error) {
        resp, err := http.Get("http://payment-service:8080/charge?order=" + orderID)
        if err != nil {
            return nil, err
        }
        defer resp.Body.Close()

        if resp.StatusCode >= 500 {
            return nil, fmt.Errorf("server error: %d", resp.StatusCode)
        }

        return io.ReadAll(resp.Body)
    })

    if err != nil {
        // Fallback: return cached/default response
        fmt.Printf("Payment service unavailable: %v, using fallback\n", err)
        return []byte(`{"status": "pending", "message": "will retry"}`), nil
    }

    return result, nil
}

func main() {
    for i := 0; i < 20; i++ {
        result, _ := callPaymentService("order-123")
        fmt.Printf("Request %d: %s\n", i+1, string(result))
        time.Sleep(500 * time.Millisecond)
    }
}
```

## Best Practices
```
best_practices:
  design:
    - "Start with a monolith, extract microservices when boundaries are clear"
    - "Define service boundaries around business capabilities (DDD bounded contexts)"
    - "Keep services small but not too small (avoid nano-services)"
    - "Each service should be deployable by a single team"

  communication:
    - "Prefer async (events) over sync (HTTP/gRPC) for loose coupling"
    - "Use sync only when client needs immediate response"
    - "Always set timeouts on inter-service calls"
    - "Implement circuit breakers for all external calls"
    - "Use retries with exponential backoff and jitter"

  data:
    - "Database per service - never share databases"
    - "Accept eventual consistency as the default"
    - "Use the outbox pattern for reliable event publishing"
    - "Design idempotent APIs and consumers"

  operations:
    - "Centralized logging with correlation IDs"
    - "Distributed tracing (Jaeger, OpenTelemetry)"
    - "Health check endpoints on every service"
    - "CI/CD per service (independent pipelines)"
    - "Containerize everything (Docker + Kubernetes)"

  anti_patterns:
    - "Distributed monolith: microservices that must deploy together"
    - "Shared database: services accessing same tables"
    - "Chatty services: too many sync calls for one operation"
    - "No API gateway: clients calling services directly"
    - "Big Bang migration: rewriting everything at once"
```

## Tags
```
tags:
  - microservices
  - architecture
  - distributed-systems
  - grpc
  - system-design
  - saga-pattern
```
