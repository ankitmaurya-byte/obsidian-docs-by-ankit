# SSE (Server-Sent Events)

## What is SSE
```
overview:
  full_name: Server-Sent Events
  type: Unidirectional real-time communication protocol
  direction: Server -> Client (one-way only)
  transport: HTTP (regular HTTP connection kept open)
  content_type: text/event-stream
  standard: HTML5 / W3C specification

key_features:
  - Built on plain HTTP (no special protocol like WebSocket)
  - Automatic reconnection by browser
  - Event ID tracking (resume from last event)
  - Simple text-based protocol
  - Works through firewalls and proxies
  - Native browser support via EventSource API
  - Lightweight compared to WebSockets
```

## How SSE Works
```
flow:
  1_client_request:
    description: Client sends regular HTTP GET request
    headers:
      Accept: text/event-stream
      Cache-Control: no-cache

  2_server_response:
    description: Server responds with event stream, keeps connection open
    headers:
      Content-Type: text/event-stream
      Cache-Control: no-cache
      Connection: keep-alive

  3_server_sends_events:
    description: Server writes events to the open connection
    format: |
      event: message
      id: 1
      data: {"user": "ankit", "action": "login"}

      event: notification
      id: 2
      data: You have 3 new messages

  4_connection_drop:
    description: If connection drops, browser auto-reconnects
    behavior: Sends Last-Event-ID header to resume from where it left off
```

## SSE Message Format
```
message_format:
  fields:
    data:
      description: The message payload (required)
      note: Can span multiple lines (each prefixed with "data:")
      example: |
        data: Hello World

    event:
      description: Event type name (optional, default is "message")
      example: |
        event: notification
        data: New follower

    id:
      description: Event ID for reconnection tracking (optional)
      example: |
        id: 42
        data: Some data

    retry:
      description: Reconnection time in milliseconds (optional)
      example: |
        retry: 5000

  rules:
    - Each field on its own line
    - Events separated by blank line (double newline)
    - Lines starting with ":" are comments (used as keep-alive)
    - UTF-8 encoded text only (no binary data)

  examples:
    simple_message:
      format: |
        data: Hello World

    json_data:
      format: |
        data: {"temperature": 22.5, "humidity": 65}

    named_event:
      format: |
        event: price-update
        data: {"symbol": "AAPL", "price": 150.25}

    multiline_data:
      format: |
        data: first line
        data: second line
        data: third line

    with_id_and_retry:
      format: |
        id: 100
        retry: 3000
        event: status
        data: Server is healthy

    keep_alive_comment:
      format: |
        : this is a comment, used as heartbeat
```

## When to Use SSE
```
use_cases:
  live_notifications:
    description: Push notifications to users in real-time
    why: Server pushes updates, no polling needed
    example: "You have a new message", "Order shipped"

  live_feeds:
    description: Real-time data feeds (news, social, stocks)
    why: Continuous stream of updates from server
    example: Twitter-like live feed, stock ticker

  progress_updates:
    description: Long-running task progress
    why: Server sends percentage updates as task progresses
    example: File upload processing, data import status

  dashboard_metrics:
    description: Live dashboards with auto-updating numbers
    why: Push metrics as they change
    example: Real-time analytics, server monitoring

  ai_streaming:
    description: Stream AI/LLM responses token by token
    why: Show response as it generates, don't wait for full response
    example: ChatGPT-style streaming responses

  log_streaming:
    description: Stream application logs in real-time
    why: Tail logs in browser without page refresh
    example: CI/CD build logs, server log viewer
```

## When NOT to Use SSE
```
avoid_when:
  - Need bidirectional communication -> use WebSockets
  - Need to send binary data -> use WebSockets
  - Need client-to-server streaming -> use WebSockets
  - Need multiplayer gaming or real-time collaboration -> use WebSockets
  - Need support on very old browsers -> use polling
  - HTTP/1.1 with many tabs (browser limits ~6 connections per domain)
```

## SSE vs WebSockets vs Polling
```
comparison:
  sse:
    direction: Server -> Client only
    protocol: HTTP
    reconnection: Automatic (built-in)
    data_format: Text only (UTF-8)
    complexity: Very simple
    browser_support: Native EventSource API
    through_proxies: Yes (plain HTTP)
    best_for: Notifications, feeds, progress, streaming text

  websocket:
    direction: Bidirectional (both ways)
    protocol: WS/WSS (upgrade from HTTP)
    reconnection: Manual (must implement)
    data_format: Text and binary
    complexity: Moderate
    browser_support: Native WebSocket API
    through_proxies: Sometimes issues with older proxies
    best_for: Chat, gaming, collaboration, real-time apps

  long_polling:
    direction: Server -> Client (simulated)
    protocol: HTTP
    reconnection: Manual (new request after each response)
    data_format: Any HTTP content type
    complexity: Simple but wasteful
    browser_support: Universal (just AJAX)
    through_proxies: Yes
    best_for: Fallback when SSE/WS not available

  short_polling:
    direction: Client polls Server repeatedly
    protocol: HTTP
    reconnection: Not applicable (always reconnecting)
    data_format: Any HTTP content type
    complexity: Simplest but most wasteful
    browser_support: Universal
    through_proxies: Yes
    best_for: Very low frequency updates (every 30s+)
```

## Code Examples

### Server in Go (net/http)
```go
package main

import (
    "fmt"
    "net/http"
    "time"
)

func sseHandler(w http.ResponseWriter, r *http.Request) {
    // Set SSE headers
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    w.Header().Set("Access-Control-Allow-Origin", "*")

    // Get the flusher for streaming
    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "Streaming not supported", http.StatusInternalServerError)
        return
    }

    // Send events every 2 seconds
    id := 0
    for {
        select {
        case <-r.Context().Done():
            fmt.Println("Client disconnected")
            return
        default:
            id++
            fmt.Fprintf(w, "id: %d\n", id)
            fmt.Fprintf(w, "event: message\n")
            fmt.Fprintf(w, "data: {\"time\": \"%s\", \"count\": %d}\n\n", time.Now().Format(time.RFC3339), id)
            flusher.Flush()
            time.Sleep(2 * time.Second)
        }
    }
}

func main() {
    http.HandleFunc("/events", sseHandler)
    fmt.Println("SSE server on :8080")
    http.ListenAndServe(":8080", nil)
}
```

### Server in Go (with broadcast to multiple clients)
```go
package main

import (
    "fmt"
    "net/http"
    "sync"
    "time"
)

type Broker struct {
    clients    map[chan string]bool
    mu         sync.RWMutex
}

func NewBroker() *Broker {
    return &Broker{clients: make(map[chan string]bool)}
}

func (b *Broker) Subscribe() chan string {
    ch := make(chan string, 10)
    b.mu.Lock()
    b.clients[ch] = true
    b.mu.Unlock()
    return ch
}

func (b *Broker) Unsubscribe(ch chan string) {
    b.mu.Lock()
    delete(b.clients, ch)
    close(ch)
    b.mu.Unlock()
}

func (b *Broker) Broadcast(msg string) {
    b.mu.RLock()
    for ch := range b.clients {
        select {
        case ch <- msg:
        default: // skip slow clients
        }
    }
    b.mu.RUnlock()
}

func main() {
    broker := NewBroker()

    // Background: generate events
    go func() {
        i := 0
        for {
            i++
            broker.Broadcast(fmt.Sprintf(`{"event":"tick","count":%d}`, i))
            time.Sleep(1 * time.Second)
        }
    }()

    http.HandleFunc("/events", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "text/event-stream")
        w.Header().Set("Cache-Control", "no-cache")
        w.Header().Set("Connection", "keep-alive")
        flusher := w.(http.Flusher)

        ch := broker.Subscribe()
        defer broker.Unsubscribe(ch)

        for {
            select {
            case msg := <-ch:
                fmt.Fprintf(w, "data: %s\n\n", msg)
                flusher.Flush()
            case <-r.Context().Done():
                return
            }
        }
    })

    fmt.Println("SSE server on :8080")
    http.ListenAndServe(":8080", nil)
}
```

### Client in Browser (JavaScript)
```javascript
// Basic SSE client
const eventSource = new EventSource('http://localhost:8080/events');

// Default "message" events
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    console.log('Event ID:', event.lastEventId);
};

// Named events
eventSource.addEventListener('notification', (event) => {
    console.log('Notification:', event.data);
});

eventSource.addEventListener('price-update', (event) => {
    const price = JSON.parse(event.data);
    document.getElementById('price').textContent = price.value;
});

// Connection events
eventSource.onopen = () => {
    console.log('Connected to SSE');
};

eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    if (eventSource.readyState === EventSource.CLOSED) {
        console.log('Connection closed');
    }
    // Browser auto-reconnects (no manual code needed)
};

// Close connection manually
// eventSource.close();
```

### Client with fetch API (for more control)
```javascript
async function consumeSSE(url) {
    const response = await fetch(url);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                console.log('Event:', JSON.parse(data));
            }
        }
    }
}

consumeSSE('http://localhost:8080/events');
```

### Node.js Server
```javascript
const http = require('http');

const server = http.createServer((req, res) => {
    if (req.url === '/events') {
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        });

        let id = 0;
        const interval = setInterval(() => {
            id++;
            res.write(`id: ${id}\n`);
            res.write(`data: ${JSON.stringify({ time: new Date().toISOString(), count: id })}\n\n`);
        }, 2000);

        req.on('close', () => {
            clearInterval(interval);
            console.log('Client disconnected');
        });
    }
});

server.listen(8080, () => console.log('SSE server on :8080'));
```

## Small Application: Live Notification Dashboard
```
app_overview:
  name: Live Notification Dashboard
  description: |
    Real-time notification system using SSE:
    1. Backend generates events (new user, new order, error alert)
    2. SSE endpoint streams events to connected browsers
    3. Frontend dashboard updates in real-time without page refresh
```

### Full Application
```go
package main

import (
    "encoding/json"
    "fmt"
    "math/rand"
    "net/http"
    "sync"
    "time"
)

type Notification struct {
    ID        int       `json:"id"`
    Type      string    `json:"type"`
    Message   string    `json:"message"`
    Timestamp time.Time `json:"timestamp"`
}

type Hub struct {
    clients map[chan Notification]bool
    mu      sync.RWMutex
}

func NewHub() *Hub {
    return &Hub{clients: make(map[chan Notification]bool)}
}

func (h *Hub) Subscribe() chan Notification {
    ch := make(chan Notification, 20)
    h.mu.Lock()
    h.clients[ch] = true
    h.mu.Unlock()
    return ch
}

func (h *Hub) Unsubscribe(ch chan Notification) {
    h.mu.Lock()
    delete(h.clients, ch)
    close(ch)
    h.mu.Unlock()
}

func (h *Hub) Publish(n Notification) {
    h.mu.RLock()
    for ch := range h.clients {
        select {
        case ch <- n:
        default:
        }
    }
    h.mu.RUnlock()
}

var hub = NewHub()

func sseHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    w.Header().Set("Access-Control-Allow-Origin", "*")
    flusher := w.(http.Flusher)

    ch := hub.Subscribe()
    defer hub.Unsubscribe(ch)

    for {
        select {
        case notif := <-ch:
            data, _ := json.Marshal(notif)
            fmt.Fprintf(w, "id: %d\n", notif.ID)
            fmt.Fprintf(w, "event: %s\n", notif.Type)
            fmt.Fprintf(w, "data: %s\n\n", data)
            flusher.Flush()
        case <-r.Context().Done():
            return
        }
    }
}

func main() {
    // Simulate events
    go func() {
        types := []string{"info", "warning", "error", "success"}
        messages := []string{
            "New user registered",
            "Payment processed: $99.99",
            "Server CPU at 92%",
            "Deployment successful",
            "API rate limit reached",
            "New order #1234",
        }
        id := 0
        for {
            id++
            hub.Publish(Notification{
                ID:        id,
                Type:      types[rand.Intn(len(types))],
                Message:   messages[rand.Intn(len(messages))],
                Timestamp: time.Now(),
            })
            time.Sleep(time.Duration(1+rand.Intn(3)) * time.Second)
        }
    }()

    // Serve HTML dashboard
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "text/html")
        fmt.Fprint(w, dashboardHTML)
    })
    http.HandleFunc("/events", sseHandler)

    fmt.Println("Dashboard at http://localhost:8080")
    http.ListenAndServe(":8080", nil)
}

var dashboardHTML = `<!DOCTYPE html>
<html>
<head>
    <title>Live Notifications</title>
    <style>
        body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
        h1 { color: #00d4ff; }
        .notification { padding: 10px; margin: 5px 0; border-radius: 4px; }
        .info { background: #0f3460; border-left: 4px solid #00d4ff; }
        .warning { background: #553c00; border-left: 4px solid #ffa500; }
        .error { background: #4a0000; border-left: 4px solid #ff4444; }
        .success { background: #003c00; border-left: 4px solid #44ff44; }
        .time { color: #888; font-size: 0.8em; }
        #count { color: #00d4ff; }
    </style>
</head>
<body>
    <h1>Live Notifications Dashboard</h1>
    <p>Connected clients receiving SSE | Events received: <span id="count">0</span></p>
    <div id="notifications"></div>
    <script>
        let count = 0;
        const es = new EventSource('/events');
        const container = document.getElementById('notifications');

        ['info', 'warning', 'error', 'success'].forEach(type => {
            es.addEventListener(type, (e) => {
                count++;
                document.getElementById('count').textContent = count;
                const data = JSON.parse(e.data);
                const div = document.createElement('div');
                div.className = 'notification ' + type;
                div.innerHTML = '<strong>[' + type.toUpperCase() + ']</strong> ' +
                    data.message + ' <span class="time">' + new Date(data.timestamp).toLocaleTimeString() + '</span>';
                container.prepend(div);
                if (container.children.length > 50) container.lastChild.remove();
            });
        });

        es.onerror = () => console.log('Reconnecting...');
    </script>
</body>
</html>`
```

## Tags
```
tags:
  - sse
  - server-sent-events
  - real-time
  - streaming
  - http
  - event-stream
```
