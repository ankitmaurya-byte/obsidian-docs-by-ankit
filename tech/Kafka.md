# Kafka

## What is Kafka
```
overview:
  full_name: Apache Kafka
  type: Distributed event streaming platform
  use_as:
    - Message broker
    - Event streaming
    - Data pipeline
    - Activity tracking
    - Log aggregation
  written_in: Java, Scala
  license: Apache 2.0
  default_port: 9092
  protocol: Custom binary protocol over TCP

key_features:
  - High throughput (millions of messages/sec)
  - Distributed and fault-tolerant
  - Durable message storage on disk
  - Consumer groups for parallel processing
  - Exactly-once semantics
  - Stream processing with Kafka Streams
  - Schema registry for data governance
  - Horizontal scaling via partitions
```

## Core Concepts
```
architecture:
  broker:
    description: A single Kafka server that stores data and serves clients
    role: Receives messages from producers, stores on disk, serves to consumers

  topic:
    description: A named feed/category of messages
    analogy: Like a database table or a folder in a filesystem
    example: "user-signups", "order-events", "payment-transactions"

  partition:
    description: A topic is split into partitions for parallelism
    properties:
      - Ordered within a single partition
      - Each message gets an offset (sequential ID)
      - Distributed across brokers
      - Partition count set at topic creation

  producer:
    description: Client that publishes messages to topics
    key_behavior: Chooses partition via key hash or round-robin

  consumer:
    description: Client that reads messages from topics
    key_behavior: Tracks offset to know what has been read

  consumer_group:
    description: Group of consumers that share the work of reading a topic
    rule: Each partition is consumed by exactly one consumer in the group
    example: 3 partitions + 3 consumers = each reads 1 partition

  zookeeper_kraft:
    zookeeper: Legacy metadata manager (being replaced)
    kraft: New built-in consensus protocol (Kafka 3.3+)
```

## When to Use Kafka
```
use_cases:
  event_streaming:
    description: Process real-time event streams
    why: High throughput, durable storage, replay capability
    example: Track user clickstream across a website

  microservice_communication:
    description: Decouple services via async messaging
    why: Services don't need to know about each other
    example: Order service publishes "order.created", inventory service consumes it

  log_aggregation:
    description: Collect logs from multiple services into one place
    why: Replaces file-based log collection, centralized and scalable
    example: All microservices publish logs to "app-logs" topic

  data_pipelines:
    description: Move data between systems (DB -> warehouse, API -> analytics)
    why: Reliable, scalable, supports connectors via Kafka Connect
    example: CDC from PostgreSQL to Elasticsearch using Debezium

  activity_tracking:
    description: Track user actions for analytics or recommendations
    why: High write throughput, can handle millions of events
    example: LinkedIn-style activity feed (page views, clicks, searches)

  metrics_monitoring:
    description: Collect and aggregate operational metrics
    why: Time-series friendly, supports windowed aggregations
    example: Aggregate server CPU/memory metrics every 30 seconds
```

## When NOT to Use Kafka
```
avoid_when:
  - Simple task queue (use RabbitMQ or Redis instead)
  - Small scale with few messages per day
  - Need strict message ordering across all messages (Kafka orders per partition only)
  - Request-reply pattern (Kafka is pub/sub, not RPC)
  - Low latency requirement under 1ms (Redis is better)
```

## Kafka vs Others
```
comparison:
  kafka_vs_rabbitmq:
    kafka:
      - Log-based, messages persist on disk
      - Consumer pulls messages
      - Replay old messages anytime
      - Better for high throughput streams
    rabbitmq:
      - Queue-based, messages deleted after consumption
      - Broker pushes messages to consumers
      - No replay (once consumed, gone)
      - Better for task distribution and routing

  kafka_vs_redis_pubsub:
    kafka:
      - Durable, messages stored on disk
      - Consumers can catch up after downtime
      - Consumer groups for load balancing
    redis:
      - In-memory, fire-and-forget
      - If consumer is offline, message is lost
      - Simpler, lower latency for small scale
```

## Installation & Setup
```
docker_setup:
  docker_compose:
    file: docker-compose.yml
    content: |
      version: '3.8'
      services:
        kafka:
          image: confluentinc/cp-kafka:7.5.0
          ports:
            - "9092:9092"
          environment:
            KAFKA_NODE_ID: 1
            KAFKA_PROCESS_ROLES: broker,controller
            KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
            KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
            KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
            KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
            KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
            CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
    run: docker compose up -d
```

## CLI Commands
```
kafka_cli:
  topics:
    create:
      command: kafka-topics --create --topic my-topic --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092
      description: Create a new topic with 3 partitions

    list:
      command: kafka-topics --list --bootstrap-server localhost:9092
      description: List all topics

    describe:
      command: kafka-topics --describe --topic my-topic --bootstrap-server localhost:9092
      description: Show topic details (partitions, replicas, ISR)

    delete:
      command: kafka-topics --delete --topic my-topic --bootstrap-server localhost:9092

  produce:
    command: kafka-console-producer --topic my-topic --bootstrap-server localhost:9092
    description: Opens interactive producer (type messages, press Enter to send)

  consume:
    from_beginning:
      command: kafka-console-consumer --topic my-topic --from-beginning --bootstrap-server localhost:9092
    from_now:
      command: kafka-console-consumer --topic my-topic --bootstrap-server localhost:9092
    with_group:
      command: kafka-console-consumer --topic my-topic --group my-group --bootstrap-server localhost:9092

  consumer_groups:
    list:
      command: kafka-consumer-groups --list --bootstrap-server localhost:9092
    describe:
      command: kafka-consumer-groups --describe --group my-group --bootstrap-server localhost:9092
      shows: current offset, log end offset, lag per partition
```

## Code Examples

### Producer in Go
```go
package main

import (
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    producer, err := kafka.NewProducer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
    })
    if err != nil {
        panic(err)
    }
    defer producer.Close()

    topic := "user-events"

    // Produce a message
    err = producer.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:            []byte("user-123"),
        Value:          []byte(`{"event":"signup","user":"ankit"}`),
    }, nil)

    // Wait for delivery confirmation
    e := <-producer.Events()
    msg := e.(*kafka.Message)
    if msg.TopicPartition.Error != nil {
        fmt.Printf("Delivery failed: %v\n", msg.TopicPartition.Error)
    } else {
        fmt.Printf("Delivered to %v [%d] at offset %v\n",
            *msg.TopicPartition.Topic, msg.TopicPartition.Partition, msg.TopicPartition.Offset)
    }
}
```

### Consumer in Go
```go
package main

import (
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "group.id":          "my-consumer-group",
        "auto.offset.reset": "earliest",
    })
    if err != nil {
        panic(err)
    }
    defer consumer.Close()

    consumer.SubscribeTopics([]string{"user-events"}, nil)

    for {
        msg, err := consumer.ReadMessage(-1) // block forever
        if err != nil {
            fmt.Printf("Consumer error: %v\n", err)
            continue
        }
        fmt.Printf("Received: key=%s value=%s partition=%d offset=%d\n",
            string(msg.Key), string(msg.Value),
            msg.TopicPartition.Partition, msg.TopicPartition.Offset)
    }
}
```

### Producer in Node.js
```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
    clientId: 'my-app',
    brokers: ['localhost:9092'],
});

const producer = kafka.producer();

async function sendMessage() {
    await producer.connect();
    await producer.send({
        topic: 'user-events',
        messages: [
            { key: 'user-123', value: JSON.stringify({ event: 'signup', user: 'ankit' }) },
            { key: 'user-456', value: JSON.stringify({ event: 'login', user: 'john' }) },
        ],
    });
    console.log('Messages sent');
    await producer.disconnect();
}

sendMessage().catch(console.error);
```

### Consumer in Node.js
```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
    clientId: 'my-app',
    brokers: ['localhost:9092'],
});

const consumer = kafka.consumer({ groupId: 'my-group' });

async function consume() {
    await consumer.connect();
    await consumer.subscribe({ topic: 'user-events', fromBeginning: true });

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            console.log({
                topic,
                partition,
                offset: message.offset,
                key: message.key.toString(),
                value: message.value.toString(),
            });
        },
    });
}

consume().catch(console.error);
```

## Small Application: Real-Time Order Processing
```
app_overview:
  name: Order Processing Pipeline
  description: |
    E-commerce order flow using Kafka:
    1. User places order -> Order Service produces to "orders" topic
    2. Payment Service consumes "orders", processes payment, produces to "payments" topic
    3. Notification Service consumes "payments", sends email/SMS
    4. Analytics Service consumes "orders" for real-time dashboards

  architecture:
    topics:
      - orders (partitioned by user_id)
      - payments (partitioned by order_id)
      - notifications (single partition)
    consumer_groups:
      - payment-processors (3 consumers for 3 partitions)
      - notification-senders (1 consumer)
      - analytics-workers (2 consumers)
```

### Order Producer
```go
package main

import (
    "encoding/json"
    "fmt"
    "time"

    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

type Order struct {
    ID        string    `json:"id"`
    UserID    string    `json:"user_id"`
    Product   string    `json:"product"`
    Amount    float64   `json:"amount"`
    CreatedAt time.Time `json:"created_at"`
}

func main() {
    producer, _ := kafka.NewProducer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
    })
    defer producer.Close()

    topic := "orders"
    order := Order{
        ID:        "ORD-001",
        UserID:    "USR-123",
        Product:   "Laptop",
        Amount:    999.99,
        CreatedAt: time.Now(),
    }

    value, _ := json.Marshal(order)
    producer.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:            []byte(order.UserID),
        Value:          value,
    }, nil)

    producer.Flush(5000)
    fmt.Printf("Order %s published\n", order.ID)
}
```

### Payment Consumer
```go
package main

import (
    "encoding/json"
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    consumer, _ := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "group.id":          "payment-processors",
        "auto.offset.reset": "earliest",
    })
    defer consumer.Close()

    consumer.SubscribeTopics([]string{"orders"}, nil)

    fmt.Println("Payment service listening for orders...")
    for {
        msg, err := consumer.ReadMessage(-1)
        if err != nil {
            continue
        }

        var order map[string]interface{}
        json.Unmarshal(msg.Value, &order)

        fmt.Printf("Processing payment for order %s, amount: $%.2f\n",
            order["id"], order["amount"])

        // Simulate payment processing
        // In real app: call payment gateway, update DB, produce to "payments" topic
    }
}
```

## Key Configuration
```
important_configs:
  producer:
    acks:
      all: Wait for all replicas to acknowledge (safest, slowest)
      1: Wait for leader only (default)
      0: Fire and forget (fastest, may lose data)
    batch.size: 16384  # bytes, batch messages for efficiency
    linger.ms: 5       # wait up to 5ms to batch more messages
    compression.type: snappy  # compress batches (snappy, gzip, lz4, zstd)

  consumer:
    auto.offset.reset:
      earliest: Start from beginning if no committed offset
      latest: Start from newest messages only
    enable.auto.commit: true  # auto-commit offsets periodically
    auto.commit.interval.ms: 5000
    max.poll.records: 500     # max records per poll

  topic:
    retention.ms: 604800000      # 7 days default
    retention.bytes: -1          # unlimited by size
    cleanup.policy:
      delete: Remove old segments after retention
      compact: Keep latest value per key (log compaction)
    min.insync.replicas: 2       # for acks=all, how many must confirm
```

## Common Patterns
```
patterns:
  event_sourcing:
    description: Store all state changes as events in Kafka
    flow: Command -> Validate -> Produce Event -> Consumers rebuild state
    benefit: Full audit trail, can rebuild state from any point

  cqrs:
    description: Separate read and write models using Kafka
    flow: Writes go to Kafka -> Multiple consumers build read-optimized views

  dead_letter_queue:
    description: Route failed messages to a separate topic for investigation
    flow: Consumer fails -> Retry N times -> Send to "topic.DLQ"

  saga_pattern:
    description: Coordinate distributed transactions across services
    flow: Each service publishes success/failure events, orchestrator reacts
```

## Tags
```
tags:
  - kafka
  - event-streaming
  - message-broker
  - distributed-systems
  - microservices
  - data-pipeline
```
