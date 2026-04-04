# TCP & UDP

## What are TCP and UDP
```
overview:
  tcp:
    full_name: Transmission Control Protocol
    type: Connection-oriented, reliable transport protocol
    layer: Transport Layer (Layer 4 of OSI model)
    rfc: RFC 793
    key_traits:
      - Reliable delivery (guaranteed, in-order)
      - Connection-oriented (3-way handshake)
      - Flow control and congestion control
      - Error detection and retransmission
      - Full-duplex communication

  udp:
    full_name: User Datagram Protocol
    type: Connectionless, unreliable transport protocol
    layer: Transport Layer (Layer 4 of OSI model)
    rfc: RFC 768
    key_traits:
      - No connection setup (fire-and-forget)
      - No guaranteed delivery or ordering
      - No flow or congestion control
      - Minimal overhead (8-byte header vs TCP's 20-byte)
      - Faster than TCP for real-time data
```

## How TCP Works

### 3-Way Handshake (Connection Setup)
```
three_way_handshake:
  purpose: Establish a reliable connection before data transfer
  steps:
    1_SYN:
      from: Client
      to: Server
      description: Client sends SYN packet with initial sequence number (ISN)
      flag: SYN=1, seq=x

    2_SYN_ACK:
      from: Server
      to: Client
      description: Server acknowledges and sends its own SYN
      flag: SYN=1, ACK=1, seq=y, ack=x+1

    3_ACK:
      from: Client
      to: Server
      description: Client acknowledges server's SYN, connection established
      flag: ACK=1, seq=x+1, ack=y+1

  after_handshake: Data transfer begins (full-duplex)

  connection_teardown:
    method: 4-way handshake (FIN/ACK from both sides)
    steps:
      1: "Client sends FIN"
      2: "Server sends ACK"
      3: "Server sends FIN"
      4: "Client sends ACK"
```

### Reliable Delivery
```
reliable_delivery:
  sequence_numbers:
    description: Every byte of data is numbered
    purpose: Receiver can detect missing data and reorder out-of-order segments

  acknowledgments:
    description: Receiver sends ACK for received data
    cumulative_ack: ACK number means "I've received everything up to this byte"
    example: "ACK=5001 means bytes 1-5000 received"

  retransmission:
    trigger: Sender retransmits if no ACK received within timeout (RTO)
    fast_retransmit: Retransmit after 3 duplicate ACKs (don't wait for timeout)

  checksums:
    description: Every segment has a checksum to detect corruption
    action: Corrupted segments are silently dropped, triggering retransmission
```

### Flow Control
```
flow_control:
  mechanism: Sliding Window Protocol
  purpose: Prevent sender from overwhelming a slow receiver

  how_it_works:
    - Receiver advertises its "receive window" (rwnd) in every ACK
    - rwnd = how much free buffer space the receiver has
    - Sender never sends more unacknowledged data than rwnd
    - If rwnd=0, sender pauses and periodically probes

  example:
    1: "Receiver says rwnd=64KB"
    2: "Sender sends 64KB of data"
    3: "Receiver processes 32KB, says rwnd=32KB"
    4: "Sender can only send 32KB more"
```

### Congestion Control
```
congestion_control:
  purpose: Prevent sender from overwhelming the network
  mechanism: Sender maintains a "congestion window" (cwnd) separate from rwnd

  phases:
    slow_start:
      description: Start with small cwnd, double it every RTT
      initial_cwnd: "Usually 1-10 MSS (Maximum Segment Size)"
      growth: Exponential (1 -> 2 -> 4 -> 8 -> 16...)
      ends_when: cwnd reaches ssthresh (slow start threshold)

    congestion_avoidance:
      description: After ssthresh, grow cwnd linearly (+1 MSS per RTT)
      growth: Linear (much slower than slow start)
      purpose: Cautiously probe for available bandwidth

    fast_recovery:
      trigger: 3 duplicate ACKs (packet loss detected)
      action: Halve cwnd, enter congestion avoidance (skip slow start)
      note: More efficient than going back to slow start

  algorithms:
    - "Reno: Classic (slow start + congestion avoidance + fast recovery)"
    - "CUBIC: Default in Linux (better for high-bandwidth networks)"
    - "BBR: Google's algorithm (measures bandwidth and RTT directly)"

  effective_window: "min(cwnd, rwnd) = how much data sender can have in flight"
```

## How UDP Works
```
udp_details:
  simplicity:
    - No handshake (just send the datagram)
    - No connection state to maintain
    - No retransmission or ordering
    - Each datagram is independent

  header:
    size: 8 bytes (vs TCP's 20+ bytes)
    fields:
      - Source Port (16 bits)
      - Destination Port (16 bits)
      - Length (16 bits)
      - Checksum (16 bits, optional in IPv4)

  max_datagram_size:
    theoretical: 65,535 bytes (limited by 16-bit length field)
    practical: ~1,472 bytes (to avoid IP fragmentation on 1500 MTU)
```

## Ports and Sockets
```
ports_and_sockets:
  port:
    definition: 16-bit number (0-65535) identifying a process on a host
    ranges:
      well_known: "0-1023 (HTTP=80, HTTPS=443, SSH=22, DNS=53)"
      registered: "1024-49151 (MySQL=3306, PostgreSQL=5432, Redis=6379)"
      ephemeral: "49152-65535 (assigned to clients dynamically by OS)"

  socket:
    definition: Combination of IP address + port + protocol
    format: "(protocol, local_ip, local_port, remote_ip, remote_port)"
    example: "(TCP, 192.168.1.10, 52431, 93.184.216.34, 443)"

  multiplexing:
    description: Multiple connections on same port via unique socket tuples
    example: |
      Web server on port 80 can handle thousands of clients because each
      connection has a unique (client_ip, client_port) pair
```

## TCP vs UDP Comparison
```
comparison:
  tcp:
    connection: Connection-oriented (handshake required)
    reliability: Guaranteed delivery, in-order
    flow_control: Yes (sliding window)
    congestion_control: Yes (slow start, CUBIC, BBR)
    overhead: Higher (20+ byte header, ACKs, retransmissions)
    speed: Slower due to overhead
    data_boundary: Stream-based (no message boundaries)
    best_for: Web, email, file transfer, SSH, database connections

  udp:
    connection: Connectionless (no handshake)
    reliability: No guarantees (best-effort)
    flow_control: None
    congestion_control: None
    overhead: Minimal (8-byte header)
    speed: Faster, lower latency
    data_boundary: Message-based (each datagram is distinct)
    best_for: Gaming, video streaming, VoIP, DNS, IoT
```

## When to Use TCP
```
tcp_use_cases:
  web_browsing:
    why: Need complete, ordered HTML/CSS/JS delivery
    protocol: HTTP/HTTPS runs over TCP

  file_transfer:
    why: Every byte must arrive correctly
    protocol: FTP, SFTP, SCP

  email:
    why: Messages must be delivered intact
    protocol: SMTP, IMAP, POP3

  database_connections:
    why: Queries and results must be reliable
    protocol: MySQL, PostgreSQL, Redis protocols

  ssh_remote_access:
    why: Commands and responses must be in-order and complete
    protocol: SSH

  api_calls:
    why: Request-response must be reliable
    protocol: REST, gRPC, GraphQL
```

## When to Use UDP
```
udp_use_cases:
  online_gaming:
    why: Low latency matters more than perfect delivery
    note: Old position data is useless, just send the latest
    example: Player positions, game state updates

  video_streaming:
    why: A few dropped frames are acceptable, buffering is not
    protocol: RTP (Real-time Transport Protocol) over UDP
    example: Zoom, Twitch, YouTube Live

  voice_over_ip:
    why: Real-time audio cannot wait for retransmissions
    protocol: RTP/RTCP over UDP
    example: Phone calls, Discord voice chat

  dns_queries:
    why: Small request/response, need to be fast
    note: Single UDP datagram for query, single for response
    fallback: Falls back to TCP if response > 512 bytes

  iot_sensors:
    why: Lightweight, battery-efficient, occasional loss is fine
    protocol: CoAP, MQTT-SN
    example: Temperature sensor sending readings every second

  dhcp:
    why: Client doesn't have an IP yet, can't establish TCP connection
    protocol: DHCP over UDP ports 67/68
```

## Code Examples

### TCP Server in Go
```go
package main

import (
    "bufio"
    "fmt"
    "net"
    "strings"
)

func handleConnection(conn net.Conn) {
    defer conn.Close()
    fmt.Printf("Client connected: %s\n", conn.RemoteAddr())

    scanner := bufio.NewScanner(conn)
    for scanner.Scan() {
        message := scanner.Text()
        fmt.Printf("Received from %s: %s\n", conn.RemoteAddr(), message)

        // Echo back in uppercase
        response := strings.ToUpper(message) + "\n"
        conn.Write([]byte(response))
    }
    fmt.Printf("Client disconnected: %s\n", conn.RemoteAddr())
}

func main() {
    listener, err := net.Listen("tcp", ":8080")
    if err != nil {
        panic(err)
    }
    defer listener.Close()
    fmt.Println("TCP server listening on :8080")

    for {
        conn, err := listener.Accept()
        if err != nil {
            fmt.Println("Accept error:", err)
            continue
        }
        go handleConnection(conn) // handle each client in a goroutine
    }
}
```

### TCP Client in Go
```go
package main

import (
    "bufio"
    "fmt"
    "net"
    "os"
)

func main() {
    conn, err := net.Dial("tcp", "localhost:8080")
    if err != nil {
        panic(err)
    }
    defer conn.Close()

    // Read from server in background
    go func() {
        scanner := bufio.NewScanner(conn)
        for scanner.Scan() {
            fmt.Println("Server:", scanner.Text())
        }
    }()

    // Send user input to server
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        fmt.Fprintf(conn, "%s\n", scanner.Text())
    }
}
```

### UDP Server in Go
```go
package main

import (
    "fmt"
    "net"
)

func main() {
    addr, err := net.ResolveUDPAddr("udp", ":9090")
    if err != nil {
        panic(err)
    }

    conn, err := net.ListenUDP("udp", addr)
    if err != nil {
        panic(err)
    }
    defer conn.Close()
    fmt.Println("UDP server listening on :9090")

    buf := make([]byte, 1024)
    for {
        n, clientAddr, err := conn.ReadFromUDP(buf)
        if err != nil {
            fmt.Println("Read error:", err)
            continue
        }

        message := string(buf[:n])
        fmt.Printf("Received from %s: %s\n", clientAddr, message)

        // Echo back
        response := []byte("ACK: " + message)
        conn.WriteToUDP(response, clientAddr)
    }
}
```

### UDP Client in Go
```go
package main

import (
    "fmt"
    "net"
)

func main() {
    addr, err := net.ResolveUDPAddr("udp", "localhost:9090")
    if err != nil {
        panic(err)
    }

    conn, err := net.DialUDP("udp", nil, addr)
    if err != nil {
        panic(err)
    }
    defer conn.Close()

    // Send a message
    message := []byte("Hello UDP Server!")
    conn.Write(message)

    // Receive response
    buf := make([]byte, 1024)
    n, err := conn.Read(buf)
    if err != nil {
        panic(err)
    }
    fmt.Println("Server response:", string(buf[:n]))
}
```

### TCP Server in Node.js
```javascript
const net = require('net');

const server = net.createServer((socket) => {
    console.log(`Client connected: ${socket.remoteAddress}:${socket.remotePort}`);

    socket.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`Received: ${message}`);
        socket.write(message.toUpperCase() + '\n'); // echo uppercase
    });

    socket.on('end', () => {
        console.log('Client disconnected');
    });

    socket.on('error', (err) => {
        console.error('Socket error:', err.message);
    });
});

server.listen(8080, () => {
    console.log('TCP server listening on :8080');
});
```

### UDP Server in Node.js
```javascript
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

server.on('message', (msg, rinfo) => {
    console.log(`Received from ${rinfo.address}:${rinfo.port}: ${msg}`);
    const response = Buffer.from('ACK: ' + msg.toString());
    server.send(response, rinfo.port, rinfo.address);
});

server.on('listening', () => {
    const addr = server.address();
    console.log(`UDP server listening on ${addr.address}:${addr.port}`);
});

server.bind(9090);
```

## Tags
```
tags:
  - tcp
  - udp
  - networking
  - transport-layer
  - sockets
  - ports
  - three-way-handshake
  - flow-control
  - congestion-control
```
