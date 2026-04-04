# Message Queues

## What are Message Queues
```
overview:
  definition: |
    A message queue is a communication mechanism where applications
    send messages to a queue, and other applications read from it.
    The sender and receiver don't need to interact at the same time.
  type: Asynchronous communication pattern
  also_known_as:
    - Message broker
    - Message-oriented middleware (MOM)
    - Event bus

key_principles:
  asynchronous: Sender doesn't wait for receiver to process
  decoupled: Producer and consumer don't know about each other
  buffered: Queue stores messages until consumed
  reliable: Messages persist even if consumer is temporarily down
```

## Why Use Message Queues
```
problems_solved:
  tight_coupling:
    without_queue: Service A calls Service B directly -> if B is down, A fails
    with_queue: Service A sends to queue -> B reads when ready -> A never fails

  traffic_spikes:
    without_queue: 10,000 requests/sec hit your API and database simultaneously
    with_queue: Queue absorbs spike, workers process at sustainable rate

  sync_bottleneck:
    without_queue: User waits 30s while server sends email + resizes image + updates analytics
    with_queue: User gets instant response, background workers handle the rest

  scaling:
    without_queue: One server does everything, can't scale parts independently
    with_queue: Add more consumers for bottleneck tasks, leave others as-is
```

## Core Concepts
```
concepts:
  message:
    description: Unit of data sent through the queue
    contains:
      - body/payload (the actual data, often JSON)
      - headers/metadata (routing info, content type, priority)
      - id (unique identifier)
    example:
      body: '{"user_id": "123", "action": "send_welcome_email"}'
      headers:
        content_type: application/json
        priority: 5

  producer:
    description: Application that creates and sends messages
    also_called: Publisher, sender
    responsibility: Serialize data, choose destination queue/topic

  consumer:
    description: Application that reads and processes messages
    also_called: Subscriber, receiver, worker
    responsibility: Deserialize data, process it, acknowledge completion

  queue:
    description: FIFO buffer that holds messages
    behavior: First In First Out (usually)
    properties:
      - Messages wait in queue until consumed
      - Can have multiple consumers (load balancing)
      - Can be durable (survives broker restart)

  topic:
    description: Named channel for pub/sub messaging
    behavior: All subscribers receive a copy of each message
    difference_from_queue: Queue delivers to ONE consumer, topic to ALL subscribers

  acknowledgment:
    description: Consumer tells broker it successfully processed a message
    types:
      ack: "I processed it successfully, remove from queue"
      nack: "I failed, requeue or send to dead letter queue"
      reject: "I can't handle this, remove it"
    why_important: Prevents message loss if consumer crashes mid-processing
```

## Messaging Patterns
```
patterns:
  point_to_point:
    description: One producer sends to one queue, one consumer reads
    delivery: Each message consumed by exactly one consumer
    use_case: Task processing, work distribution
    diagram: |
      Producer -> [Queue] -> Consumer

  work_queue:
    description: Multiple consumers share the work from one queue
    delivery: Each message goes to one consumer (round-robin)
    use_case: Parallel processing, load distribution
    diagram: |
      Producer -> [Queue] -> Consumer 1
                          -> Consumer 2
                          -> Consumer 3

  publish_subscribe:
    description: One producer broadcasts to many consumers
    delivery: Each consumer gets a copy of every message
    use_case: Event notifications, real-time updates
    diagram: |
      Producer -> [Topic] -> Subscriber 1
                          -> Subscriber 2
                          -> Subscriber 3

  request_reply:
    description: Send a request message, get a response on a reply queue
    delivery: Synchronous-like pattern over async infrastructure
    use_case: RPC over message queues
    diagram: |
      Client -> [Request Queue] -> Server
      Client <- [Reply Queue]   <- Server

  dead_letter:
    description: Failed messages routed to a separate queue for inspection
    delivery: After N retries, message moves to DLQ
    use_case: Error handling, debugging, retry logic
    diagram: |
      [Main Queue] -> Consumer (fails)
                   -> [Dead Letter Queue] -> Manual inspection
```

## Delivery Guarantees
```
delivery_semantics:
  at_most_once:
    description: Message delivered 0 or 1 times (may be lost)
    how: Send and forget, no acknowledgment
    trade_off: Fastest, but may lose messages
    use_case: Metrics, logs where occasional loss is acceptable

  at_least_once:
    description: Message delivered 1 or more times (may be duplicated)
    how: Retry until acknowledged
    trade_off: No message loss, but consumer must handle duplicates
    use_case: Most business applications (with idempotent consumers)

  exactly_once:
    description: Message delivered exactly 1 time
    how: Transactions + deduplication (complex)
    trade_off: Slowest, most complex, highest guarantee
    use_case: Financial transactions, critical data
    note: Very hard to achieve truly; usually "effectively once" via idempotency
```

## Comparison of Message Queue Technologies
```
comparison:
  rabbitmq:
    type: Traditional message broker
    protocol: AMQP
    model: Smart broker, push to consumers
    routing: Complex (direct, fanout, topic, headers exchanges)
    persistence: Messages deleted after consumption
    throughput: ~50K msgs/sec
    best_for: Task queues, complex routing, RPC
    language: Erlang

  kafka:
    type: Distributed event streaming platform
    protocol: Custom binary
    model: Dumb broker, consumers pull
    routing: Topic + partition based
    persistence: Messages stored on disk for configurable period
    throughput: ~1M msgs/sec
    best_for: Event streaming, data pipelines, log aggregation
    language: Java/Scala

  redis_streams:
    type: In-memory data store with streaming
    protocol: RESP
    model: Consumer groups with pull
    routing: Stream key based
    persistence: In-memory with optional disk persistence
    throughput: ~500K msgs/sec
    best_for: Simple queues, low latency, caching + messaging combo
    language: C

  amazon_sqs:
    type: Managed cloud queue service
    protocol: HTTP/HTTPS
    model: Pull-based
    routing: Queue-based only
    persistence: Managed by AWS
    throughput: Virtually unlimited (managed)
    best_for: AWS-native apps, serverless, simple queuing
    language: Managed service

  nats:
    type: Cloud-native messaging system
    protocol: Custom text-based
    model: Pub/Sub with optional persistence (JetStream)
    routing: Subject-based with wildcards
    persistence: Optional with JetStream
    throughput: ~10M msgs/sec
    best_for: Microservices, IoT, edge computing
    language: Go
```

## How to Choose
```
decision_guide:
  need_complex_routing: RabbitMQ
  need_message_replay: Kafka
  need_high_throughput_streaming: Kafka
  need_simple_task_queue: RabbitMQ or Redis
  need_low_latency: Redis Streams or NATS
  need_managed_service: Amazon SQS or Google Pub/Sub
  need_cloud_native_lightweight: NATS
  already_using_redis: Redis Streams
  need_exactly_once: Kafka (with transactions)
```

## Common Implementation Patterns
```
best_practices:
  idempotent_consumers:
    description: Design consumers to handle duplicate messages safely
    how: Use message ID or business key to detect duplicates
    example: |
      // Before processing, check if already handled
      if db.Exists("processed_messages", msg.ID) {
          msg.Ack()
          return // already processed
      }
      process(msg)
      db.Insert("processed_messages", msg.ID)
      msg.Ack()

  retry_with_backoff:
    description: Retry failed messages with increasing delays
    strategy:
      attempt_1: Wait 1 second
      attempt_2: Wait 5 seconds
      attempt_3: Wait 30 seconds
      after_max_retries: Send to dead letter queue

  poison_message_handling:
    description: Messages that always fail should be removed
    how: Track retry count, move to DLQ after threshold
    why: Prevents one bad message from blocking the entire queue

  message_ordering:
    description: Ensure related messages are processed in order
    how: Use partition keys (Kafka) or single consumer per queue
    example: All events for user-123 go to same partition

  graceful_shutdown:
    description: Stop consuming new messages, finish processing current ones
    how: |
      1. Stop accepting new messages
      2. Wait for in-flight messages to complete
      3. Acknowledge all processed messages
      4. Close connection
```

## Simple Queue Example in Go
```go
// Using channels as a simple in-process message queue
package main

import (
    "fmt"
    "sync"
    "time"
)

type Message struct {
    ID   int
    Body string
}

func producer(queue chan<- Message, wg *sync.WaitGroup) {
    defer wg.Done()
    for i := 1; i <= 5; i++ {
        msg := Message{ID: i, Body: fmt.Sprintf("Task %d", i)}
        queue <- msg
        fmt.Printf("Produced: %s\n", msg.Body)
    }
    close(queue)
}

func consumer(id int, queue <-chan Message, wg *sync.WaitGroup) {
    defer wg.Done()
    for msg := range queue {
        fmt.Printf("Consumer %d processing: %s\n", id, msg.Body)
        time.Sleep(500 * time.Millisecond) // simulate work
        fmt.Printf("Consumer %d done with: %s\n", id, msg.Body)
    }
}

func main() {
    queue := make(chan Message, 10) // buffered channel = message queue
    var wg sync.WaitGroup

    // Start 3 consumers (workers)
    for i := 1; i <= 3; i++ {
        wg.Add(1)
        go consumer(i, queue, &wg)
    }

    // Start producer
    wg.Add(1)
    go producer(queue, &wg)

    wg.Wait()
    fmt.Println("All messages processed")
}
```

## Tags
```
tags:
  - message-queue
  - async-processing
  - distributed-systems
  - microservices
  - architecture-pattern
```
