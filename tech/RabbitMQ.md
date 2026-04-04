# RabbitMQ

## What is RabbitMQ
```
overview:
  full_name: RabbitMQ
  type: Open-source message broker
  use_as:
    - Message queue
    - Task distribution
    - Pub/Sub messaging
    - Request buffering
  written_in: Erlang
  license: Mozilla Public License 2.0
  default_port: 5672
  management_ui_port: 15672
  protocol: AMQP 0-9-1 (also supports MQTT, STOMP)

key_features:
  - Multiple messaging patterns (queues, pub/sub, routing, RPC)
  - Message acknowledgments and persistence
  - Flexible routing via exchanges
  - Dead letter queues for failed messages
  - Priority queues
  - Clustering and high availability
  - Management UI dashboard
  - Plugin ecosystem
```

## Core Concepts
```
architecture:
  producer:
    description: Application that sends messages
    sends_to: Exchange (never directly to a queue)

  exchange:
    description: Receives messages and routes them to queues based on rules
    types:
      direct:
        description: Routes to queue with exact matching routing key
        use_case: Task distribution to specific workers
        example: routing_key="pdf" -> goes to pdf-processing queue
      fanout:
        description: Broadcasts to ALL bound queues (ignores routing key)
        use_case: Pub/Sub, notifications to all services
        example: New user event sent to email, analytics, and welcome queues
      topic:
        description: Routes based on pattern matching with wildcards
        wildcards:
          "*": Matches exactly one word
          "#": Matches zero or more words
        example: "order.*.created" matches "order.us.created" and "order.eu.created"
      headers:
        description: Routes based on message headers instead of routing key
        use_case: Complex routing based on multiple attributes

  queue:
    description: Buffer that stores messages until consumed
    properties:
      - Durable (survives broker restart)
      - Exclusive (used by one connection only)
      - Auto-delete (deleted when last consumer disconnects)
      - TTL (messages expire after time)

  binding:
    description: Rule that links an exchange to a queue
    has: routing key or pattern

  consumer:
    description: Application that receives messages from a queue
    modes:
      push: Broker delivers messages to consumer (basic_consume)
      pull: Consumer explicitly fetches messages (basic_get)

  message:
    properties:
      - body (payload)
      - routing_key
      - delivery_mode (1=transient, 2=persistent)
      - content_type
      - headers
      - priority (0-255)
      - expiration (TTL)
```

## When to Use RabbitMQ
```
use_cases:
  task_queues:
    description: Distribute work across multiple workers
    why: Built-in load balancing, ack/nack, retry
    example: Image resizing - upload service queues jobs, worker pool processes them

  async_processing:
    description: Offload slow operations from request cycle
    why: User gets instant response, background worker handles heavy work
    example: User signs up -> API responds 200 -> RabbitMQ delivers to email service

  service_decoupling:
    description: Services communicate without direct dependencies
    why: Producer doesn't need to know about consumers
    example: Order service sends event, shipping and billing consume independently

  rate_limiting_buffering:
    description: Buffer bursts of traffic for downstream services
    why: Queue absorbs spikes, consumers process at their own pace
    example: Black Friday traffic spike -> queue buffers -> payment service processes steadily

  rpc_over_messages:
    description: Request-reply pattern using queues
    why: Async RPC with retries and persistence
    example: Client sends request with reply_to queue, server responds to that queue

  scheduled_tasks:
    description: Delay message delivery using TTL + dead letter exchange
    why: No need for external scheduler
    example: Send reminder email 24 hours after signup
```

## When NOT to Use RabbitMQ
```
avoid_when:
  - Need to replay old messages (RabbitMQ deletes after consumption)
  - Need very high throughput (millions/sec) -> use Kafka
  - Need long-term message storage -> use Kafka
  - Simple pub/sub with no persistence needed -> use Redis Pub/Sub
  - Need stream processing -> use Kafka Streams
```

## RabbitMQ vs Kafka
```
comparison:
  rabbitmq:
    model: Smart broker, dumb consumer
    delivery: Broker pushes to consumers
    message_lifecycle: Deleted after acknowledgment
    ordering: Per-queue ordering guaranteed
    routing: Complex routing via exchange types
    best_for: Task distribution, RPC, complex routing
    throughput: Thousands to tens of thousands/sec

  kafka:
    model: Dumb broker, smart consumer
    delivery: Consumer pulls from broker
    message_lifecycle: Retained on disk for configured period
    ordering: Per-partition ordering only
    routing: Topic-based only
    best_for: Event streaming, log aggregation, data pipelines
    throughput: Millions/sec
```

## Installation & Setup
```
docker_setup:
  docker_compose:
    file: docker-compose.yml
    content: |
      version: '3.8'
      services:
        rabbitmq:
          image: rabbitmq:3-management
          ports:
            - "5672:5672"
            - "15672:15672"
          environment:
            RABBITMQ_DEFAULT_USER: guest
            RABBITMQ_DEFAULT_PASS: guest
          volumes:
            - rabbitmq_data:/var/lib/rabbitmq
      volumes:
        rabbitmq_data:
    run: docker compose up -d
    management_ui: http://localhost:15672 (guest/guest)
```

## CLI Commands
```
rabbitmq_cli:
  server:
    status:
      command: rabbitmqctl status
      description: Check broker status

    list_queues:
      command: rabbitmqctl list_queues name messages consumers
      description: List all queues with message count and consumers

    list_exchanges:
      command: rabbitmqctl list_exchanges name type
      description: List all exchanges

    list_bindings:
      command: rabbitmqctl list_bindings
      description: Show exchange-to-queue bindings

    list_connections:
      command: rabbitmqctl list_connections user peer_host state
      description: Show active connections

  queue_management:
    purge:
      command: rabbitmqctl purge_queue my-queue
      description: Delete all messages in a queue

    delete:
      command: rabbitmqctl delete_queue my-queue
      description: Delete a queue

  plugins:
    enable:
      command: rabbitmq-plugins enable rabbitmq_management
      description: Enable management UI plugin

    list:
      command: rabbitmq-plugins list
      description: List all available plugins
```

## Code Examples

### Producer in Go
```go
package main

import (
    "fmt"
    "log"

    amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
    // Connect to RabbitMQ
    conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    // Create a channel
    ch, err := conn.Channel()
    if err != nil {
        log.Fatal(err)
    }
    defer ch.Close()

    // Declare a queue
    q, err := ch.QueueDeclare(
        "task-queue", // name
        true,         // durable (survives restart)
        false,        // auto-delete
        false,        // exclusive
        false,        // no-wait
        nil,          // arguments
    )
    if err != nil {
        log.Fatal(err)
    }

    // Publish a message
    body := `{"task":"send_email","to":"user@example.com"}`
    err = ch.Publish(
        "",     // exchange (empty = default direct exchange)
        q.Name, // routing key (queue name)
        false,  // mandatory
        false,  // immediate
        amqp.Publishing{
            DeliveryMode: amqp.Persistent, // message survives restart
            ContentType:  "application/json",
            Body:         []byte(body),
        },
    )
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println("Message sent:", body)
}
```

### Consumer in Go
```go
package main

import (
    "fmt"
    "log"
    "time"

    amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
    conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    ch, err := conn.Channel()
    if err != nil {
        log.Fatal(err)
    }
    defer ch.Close()

    // Declare the same queue (idempotent)
    q, err := ch.QueueDeclare("task-queue", true, false, false, false, nil)
    if err != nil {
        log.Fatal(err)
    }

    // Fair dispatch: prefetch 1 message at a time
    ch.Qos(1, 0, false)

    // Start consuming
    msgs, err := ch.Consume(
        q.Name, // queue
        "",     // consumer tag
        false,  // auto-ack (false = manual ack)
        false,  // exclusive
        false,  // no-local
        false,  // no-wait
        nil,    // args
    )
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println("Waiting for messages...")
    for msg := range msgs {
        fmt.Printf("Received: %s\n", msg.Body)

        // Simulate work
        time.Sleep(2 * time.Second)

        // Acknowledge message (removes from queue)
        msg.Ack(false)
        fmt.Println("Done processing")
    }
}
```

### Pub/Sub with Fanout Exchange
```go
// Publisher
func publishEvent(ch *amqp.Channel) {
    // Declare fanout exchange
    ch.ExchangeDeclare("user-events", "fanout", true, false, false, false, nil)

    ch.Publish(
        "user-events", // exchange
        "",            // routing key (ignored by fanout)
        false, false,
        amqp.Publishing{
            ContentType: "application/json",
            Body:        []byte(`{"event":"user.created","user_id":"123"}`),
        },
    )
}

// Subscriber (each service creates its own queue)
func subscribeEvents(ch *amqp.Channel, serviceName string) {
    ch.ExchangeDeclare("user-events", "fanout", true, false, false, false, nil)

    // Each service gets its own queue
    q, _ := ch.QueueDeclare(serviceName+"-events", true, false, false, false, nil)

    // Bind queue to exchange
    ch.QueueBind(q.Name, "", "user-events", false, nil)

    msgs, _ := ch.Consume(q.Name, "", true, false, false, false, nil)
    for msg := range msgs {
        fmt.Printf("[%s] Got event: %s\n", serviceName, msg.Body)
    }
}
```

### Node.js Example
```javascript
const amqp = require('amqplib');

// Producer
async function produce() {
    const conn = await amqp.connect('amqp://localhost');
    const ch = await conn.createChannel();

    const queue = 'task-queue';
    await ch.assertQueue(queue, { durable: true });

    const msg = JSON.stringify({ task: 'resize_image', path: '/uploads/photo.jpg' });
    ch.sendToQueue(queue, Buffer.from(msg), { persistent: true });
    console.log('Sent:', msg);

    setTimeout(() => conn.close(), 500);
}

// Consumer
async function consume() {
    const conn = await amqp.connect('amqp://localhost');
    const ch = await conn.createChannel();

    const queue = 'task-queue';
    await ch.assertQueue(queue, { durable: true });
    ch.prefetch(1);

    console.log('Waiting for messages...');
    ch.consume(queue, (msg) => {
        const content = JSON.parse(msg.content.toString());
        console.log('Processing:', content);

        // Simulate async work
        setTimeout(() => {
            ch.ack(msg);
            console.log('Done');
        }, 2000);
    });
}

produce();
consume();
```

## Small Application: Email Notification System
```
app_overview:
  name: Email Notification System
  description: |
    Decouple email sending from API using RabbitMQ:
    1. API receives request -> publishes to "emails" queue -> responds 202 Accepted
    2. Email workers consume queue, send via SMTP
    3. Failed emails go to dead letter queue for retry

  architecture:
    exchange: email-exchange (direct)
    queues:
      - emails (main queue, TTL: none)
      - emails-retry (DLQ, TTL: 60s, dead-letters back to emails)
      - emails-failed (permanent failure queue after 3 retries)
    routing_keys:
      - send (main processing)
      - retry (delayed retry)
```

### Email Worker
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"

    amqp "github.com/rabbitmq/amqp091-go"
)

type EmailTask struct {
    To      string `json:"to"`
    Subject string `json:"subject"`
    Body    string `json:"body"`
    Retries int    `json:"retries"`
}

func main() {
    conn, _ := amqp.Dial("amqp://guest:guest@localhost:5672/")
    defer conn.Close()
    ch, _ := conn.Channel()
    defer ch.Close()

    // Declare dead letter exchange for retries
    ch.ExchangeDeclare("email-dlx", "direct", true, false, false, false, nil)

    // Main queue with dead letter config
    ch.QueueDeclare("emails", true, false, false, false, amqp.Table{
        "x-dead-letter-exchange":    "email-dlx",
        "x-dead-letter-routing-key": "retry",
    })

    // Retry queue: messages wait 60s then go back to main queue
    ch.QueueDeclare("emails-retry", true, false, false, false, amqp.Table{
        "x-message-ttl":             int32(60000),
        "x-dead-letter-exchange":    "",
        "x-dead-letter-routing-key": "emails",
    })
    ch.QueueBind("emails-retry", "retry", "email-dlx", false, nil)

    ch.Qos(1, 0, false)

    msgs, _ := ch.Consume("emails", "", false, false, false, false, nil)

    fmt.Println("Email worker started...")
    for msg := range msgs {
        var task EmailTask
        json.Unmarshal(msg.Body, &task)

        fmt.Printf("Sending email to %s (attempt %d)\n", task.To, task.Retries+1)

        err := sendEmail(task)
        if err != nil {
            if task.Retries < 3 {
                task.Retries++
                body, _ := json.Marshal(task)
                // Reject message -> goes to DLQ -> waits 60s -> retries
                msg.Nack(false, false)
                fmt.Printf("Failed, will retry (attempt %d)\n", task.Retries)
                _ = body // In real app, republish with updated retry count
            } else {
                fmt.Printf("Permanently failed after 3 retries: %s\n", task.To)
                msg.Ack(false) // Remove from queue
            }
        } else {
            msg.Ack(false)
            fmt.Println("Email sent successfully")
        }
    }
}

func sendEmail(task EmailTask) error {
    // Implement SMTP sending here
    fmt.Printf("  -> To: %s, Subject: %s\n", task.To, task.Subject)
    return nil
}
```

## Common Patterns
```
patterns:
  work_queue:
    description: Distribute tasks among multiple workers
    setup: One queue, multiple consumers, prefetch=1
    ack: Manual acknowledgment after processing

  publish_subscribe:
    description: Broadcast messages to all consumers
    setup: Fanout exchange, each consumer has own queue

  routing:
    description: Selective message delivery based on routing key
    setup: Direct exchange, queues bound with specific keys

  topic_routing:
    description: Pattern-based routing with wildcards
    setup: Topic exchange with * and # wildcards

  rpc:
    description: Request-reply over queues
    setup: Reply-to queue + correlation ID in message properties

  delayed_message:
    description: Deliver message after a delay
    setup: TTL on message/queue + dead letter exchange
```

## Tags
```
tags:
  - rabbitmq
  - message-queue
  - amqp
  - async-processing
  - microservices
  - task-queue
```
