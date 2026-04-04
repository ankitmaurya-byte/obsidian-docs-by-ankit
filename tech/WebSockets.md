# WebSockets

## What are WebSockets
```
overview:
  full_name: WebSocket Protocol
  type: Full-duplex communication protocol over a single TCP connection
  standard: RFC 6455
  transport: TCP
  url_scheme: "ws:// (unencrypted) or wss:// (TLS encrypted)"
  default_ports:
    ws: 80
    wss: 443

key_features:
  - Full-duplex (both sides send/receive simultaneously)
  - Persistent connection (no repeated handshakes)
  - Low overhead per message (2-14 bytes frame header vs HTTP headers)
  - Binary and text message support
  - Works through most proxies and firewalls
  - Native browser support via WebSocket API
```

## How WebSockets Work
```
flow:
  1_http_upgrade:
    description: Client initiates WebSocket handshake via HTTP Upgrade request
    client_request: |
      GET /chat HTTP/1.1
      Host: example.com
      Upgrade: websocket
      Connection: Upgrade
      Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
      Sec-WebSocket-Version: 13

  2_server_accepts:
    description: Server responds with 101 Switching Protocols
    server_response: |
      HTTP/1.1 101 Switching Protocols
      Upgrade: websocket
      Connection: Upgrade
      Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

  3_connection_open:
    description: TCP connection is now a WebSocket connection
    behavior: Both sides can send messages at any time

  4_message_exchange:
    description: Messages sent as frames (text or binary)
    note: No HTTP overhead per message

  5_close_handshake:
    description: Either side sends close frame
    behavior: Other side responds with close frame, TCP connection closed
```

## WebSocket Frames
```
frames:
  structure:
    fin_bit: "1 = final fragment, 0 = more fragments follow"
    opcode: "Type of frame"
    mask_bit: "Client-to-server frames must be masked"
    payload_length: "7 bits, 16 bits, or 64 bits depending on size"
    payload: "The actual data"

  opcodes:
    0x0: "Continuation frame"
    0x1: "Text frame (UTF-8)"
    0x2: "Binary frame"
    0x8: "Connection close"
    0x9: "Ping"
    0xA: "Pong"

  ping_pong:
    purpose: Keep-alive mechanism to detect dead connections
    behavior:
      - Either side can send Ping
      - Receiver must respond with Pong
      - If no Pong received, connection is dead
```

## WebSocket vs SSE vs Polling
```
comparison:
  websocket:
    direction: Bidirectional (full-duplex)
    protocol: WebSocket (ws://, wss://)
    connection: Persistent
    overhead: Very low (2-14 bytes per frame)
    binary_support: Yes
    auto_reconnect: No (must implement manually)
    browser_support: All modern browsers
    use_cases:
      - Chat applications
      - Multiplayer games
      - Collaborative editing
      - Financial trading dashboards

  sse:
    direction: Unidirectional (server to client only)
    protocol: HTTP (text/event-stream)
    connection: Persistent
    overhead: Low (text-based event format)
    binary_support: No (text only)
    auto_reconnect: Yes (built into EventSource API)
    browser_support: All modern browsers (no IE)
    use_cases:
      - Live notifications
      - Stock price updates
      - Social media feeds
      - Server log streaming

  long_polling:
    direction: Client-initiated (simulates push)
    protocol: HTTP
    connection: New connection per response
    overhead: High (full HTTP headers each time)
    binary_support: Yes
    auto_reconnect: Manual (send new request after each response)
    browser_support: Everything
    use_cases:
      - Simple notification systems
      - Fallback when WebSocket unavailable
      - Low-frequency updates

  short_polling:
    direction: Client-initiated
    protocol: HTTP
    connection: New connection per poll
    overhead: Highest (frequent requests, mostly empty)
    how: Client sends request every N seconds
    use_cases: Simple status checks, low-frequency polling

  decision_guide:
    need_bidirectional: "WebSocket"
    server_push_only: "SSE (simpler) or WebSocket"
    low_frequency_updates: "Long polling or SSE"
    binary_data: "WebSocket"
    behind_restrictive_proxy: "SSE (plain HTTP) or long polling"
```

## When to Use WebSockets
```
use_cases:
  chat_applications:
    description: Real-time messaging between users
    why: Bidirectional, low-latency message delivery
    example: Slack, Discord, WhatsApp Web

  multiplayer_games:
    description: Real-time game state synchronization
    why: Fast bidirectional updates, binary data support
    example: Browser-based multiplayer games

  collaborative_editing:
    description: Multiple users editing same document
    why: Instant synchronization of changes
    example: Google Docs, Figma

  live_dashboards:
    description: Real-time data visualization
    why: Continuous data streaming from server
    example: Trading platforms, monitoring dashboards

  iot_device_communication:
    description: Sensor data streaming and device control
    why: Persistent connection, low overhead per message

avoid_when:
  - Simple request-response API (use REST)
  - Server-only push with no client messages (use SSE)
  - Infrequent updates (polling is simpler)
  - Need HTTP caching (WebSocket bypasses HTTP cache)
```

## Code Examples

### WebSocket Server in Go (gorilla/websocket)
```go
package main

import (
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	// Allow all origins for development
	CheckOrigin: func(r *http.Request) bool { return true },
}

// Hub manages all active WebSocket connections
type Hub struct {
	mu      sync.RWMutex
	clients map[*websocket.Conn]string // conn -> username
}

func newHub() *Hub {
	return &Hub{
		clients: make(map[*websocket.Conn]string),
	}
}

func (h *Hub) addClient(conn *websocket.Conn, username string) {
	h.mu.Lock()
	h.clients[conn] = username
	h.mu.Unlock()
}

func (h *Hub) removeClient(conn *websocket.Conn) {
	h.mu.Lock()
	delete(h.clients, conn)
	h.mu.Unlock()
}

// Broadcast sends a message to all connected clients
func (h *Hub) broadcast(message []byte) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	for conn := range h.clients {
		if err := conn.WriteMessage(websocket.TextMessage, message); err != nil {
			log.Printf("write error: %v", err)
			conn.Close()
		}
	}
}

type ChatMessage struct {
	Type     string `json:"type"`
	Username string `json:"username"`
	Text     string `json:"text"`
}

var hub = newHub()

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("upgrade error: %v", err)
		return
	}
	defer conn.Close()

	username := r.URL.Query().Get("username")
	if username == "" {
		username = "anonymous"
	}

	hub.addClient(conn, username)
	defer hub.removeClient(conn)

	// Announce user joined
	joinMsg := `{"type":"system","text":"` + username + ` joined the chat"}`
	hub.broadcast([]byte(joinMsg))

	log.Printf("%s connected", username)

	// Read messages from this client
	for {
		_, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseNormalClosure) {
				log.Printf("read error: %v", err)
			}
			break
		}

		// Broadcast to all clients
		outMsg := `{"type":"message","username":"` + username + `","text":"` + string(message) + `"}`
		hub.broadcast([]byte(outMsg))
	}

	// Announce user left
	leaveMsg := `{"type":"system","text":"` + username + ` left the chat"}`
	hub.broadcast([]byte(leaveMsg))
}

func main() {
	http.HandleFunc("/ws", handleWebSocket)

	// Serve a simple HTML page for testing
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "index.html")
	})

	log.Println("WebSocket server on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### WebSocket Client in JavaScript
```javascript
// Connect to WebSocket server
const ws = new WebSocket("ws://localhost:8080/ws?username=ankit");

// Connection opened
ws.addEventListener("open", () => {
  console.log("Connected to chat server");
  ws.send("Hello everyone!");
});

// Receive messages
ws.addEventListener("message", (event) => {
  const msg = JSON.parse(event.data);

  if (msg.type === "system") {
    console.log(`[System] ${msg.text}`);
  } else {
    console.log(`${msg.username}: ${msg.text}`);
  }
});

// Connection closed
ws.addEventListener("close", (event) => {
  console.log(`Disconnected: code=${event.code} reason=${event.reason}`);
});

// Connection error
ws.addEventListener("error", (error) => {
  console.error("WebSocket error:", error);
});

// Send a message
function sendMessage(text) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(text);
  } else {
    console.error("WebSocket is not open");
  }
}

// Close connection gracefully
function disconnect() {
  ws.close(1000, "User disconnected");
}
```

### WebSocket Client with Auto-Reconnect in JavaScript
```javascript
class ReconnectingWebSocket {
  constructor(url, options = {}) {
    this.url = url;
    this.maxRetries = options.maxRetries || 10;
    this.retryDelay = options.retryDelay || 1000;
    this.retryCount = 0;
    this.handlers = { open: [], message: [], close: [], error: [] };
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.addEventListener("open", (e) => {
      console.log("Connected");
      this.retryCount = 0;
      this.handlers.open.forEach((fn) => fn(e));
    });

    this.ws.addEventListener("message", (e) => {
      this.handlers.message.forEach((fn) => fn(e));
    });

    this.ws.addEventListener("close", (e) => {
      this.handlers.close.forEach((fn) => fn(e));

      if (e.code !== 1000 && this.retryCount < this.maxRetries) {
        const delay = this.retryDelay * Math.pow(2, this.retryCount);
        console.log(`Reconnecting in ${delay}ms (attempt ${this.retryCount + 1})`);
        this.retryCount++;
        setTimeout(() => this.connect(), delay);
      }
    });

    this.ws.addEventListener("error", (e) => {
      this.handlers.error.forEach((fn) => fn(e));
    });
  }

  on(event, handler) {
    this.handlers[event].push(handler);
  }

  send(data) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    }
  }

  close() {
    this.ws.close(1000, "Client closing");
  }
}

// Usage
const chat = new ReconnectingWebSocket("ws://localhost:8080/ws?username=ankit", {
  maxRetries: 5,
  retryDelay: 2000,
});

chat.on("message", (event) => {
  const msg = JSON.parse(event.data);
  console.log(`${msg.username}: ${msg.text}`);
});

chat.on("open", () => chat.send("I'm back!"));
```

### Chat App HTML Page (Demo)
```
demo_html: |
  <!DOCTYPE html>
  <html>
  <head><title>WebSocket Chat</title></head>
  <body>
    <div id="messages" style="height:300px;overflow-y:scroll;border:1px solid #ccc;padding:10px;"></div>
    <input id="input" type="text" placeholder="Type a message..." style="width:80%;" />
    <button onclick="send()">Send</button>

    <script>
      const username = prompt("Enter your name:") || "anonymous";
      const ws = new WebSocket(`ws://localhost:8080/ws?username=${username}`);
      const messages = document.getElementById("messages");
      const input = document.getElementById("input");

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        const div = document.createElement("div");
        if (msg.type === "system") {
          div.style.color = "gray";
          div.textContent = msg.text;
        } else {
          div.textContent = `${msg.username}: ${msg.text}`;
        }
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
      };

      function send() {
        if (input.value) {
          ws.send(input.value);
          input.value = "";
        }
      }

      input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") send();
      });
    </script>
  </body>
  </html>
```
