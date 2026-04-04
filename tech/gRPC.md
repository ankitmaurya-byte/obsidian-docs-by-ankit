# gRPC

## What is gRPC
```
overview:
  full_name: gRPC Remote Procedure Call
  type: High-performance RPC framework
  created_by: Google (2015, open-sourced)
  transport: HTTP/2
  serialization: Protocol Buffers (protobuf) by default
  default_port: 50051 (convention, not required)

key_features:
  - Binary serialization (smaller, faster than JSON)
  - HTTP/2 multiplexing (multiple RPCs over one connection)
  - Strongly typed contracts via .proto files
  - Code generation for 10+ languages
  - Bidirectional streaming
  - Built-in deadlines, cancellation, interceptors
  - Native load balancing and service discovery support
```

## How gRPC Works
```
flow:
  1_define_proto:
    description: Define service and messages in .proto file
    note: This is the contract between client and server

  2_generate_code:
    description: Run protoc compiler to generate client/server stubs
    languages: Go, Java, Python, C++, Node.js, Rust, etc.

  3_implement_server:
    description: Implement the generated server interface with business logic

  4_client_calls:
    description: Client uses generated stub to call server methods
    behavior: Looks like a local function call, but executes on remote server

  under_the_hood:
    - Client serializes request to protobuf binary
    - Sends over HTTP/2 stream with gRPC headers
    - Server deserializes, executes handler, serializes response
    - Response sent back over same HTTP/2 connection
    - Client deserializes response
```

## Protocol Buffers
```
protobuf:
  what: Language-neutral binary serialization format
  file_extension: .proto
  version: proto3 (current, recommended)

  scalar_types:
    - "double, float"
    - "int32, int64, uint32, uint64"
    - "sint32, sint64 (more efficient for negative numbers)"
    - "bool"
    - "string"
    - "bytes"

  message_definition:
    description: Structured data type (like a struct/class)
    example: |
      syntax = "proto3";

      message User {
        int32 id = 1;            // field number, NOT default value
        string name = 2;
        string email = 3;
        Role role = 4;
        repeated string tags = 5; // list/array
        optional string bio = 6;  // explicitly optional
      }

      enum Role {
        ROLE_UNSPECIFIED = 0;     // first enum value must be 0
        ROLE_USER = 1;
        ROLE_ADMIN = 2;
      }

  field_numbers:
    description: Unique identifier for each field in binary encoding
    rules:
      - Must be unique within a message
      - 1-15 use 1 byte (use for frequently set fields)
      - 16-2047 use 2 bytes
      - Never reuse a deleted field number (use reserved)
    reserved_example: |
      message User {
        reserved 4, 8;
        reserved "old_field_name";
      }

  nested_and_repeated:
    example: |
      message Order {
        int32 id = 1;
        User customer = 2;           // nested message
        repeated OrderItem items = 3; // list of items
        map<string, string> metadata = 4; // map type
      }

      message OrderItem {
        string product_name = 1;
        int32 quantity = 2;
        double price = 3;
      }

  protobuf_vs_json:
    size: "3-10x smaller (binary encoding, no field names)"
    speed: "5-100x faster serialization/deserialization"
    readability: "Not human-readable (binary), need tools to inspect"
    schema: "Required .proto file vs optional JSON Schema"
```

## Service Definition
```
service_definition:
  description: Define RPC methods in .proto file
  example: |
    syntax = "proto3";

    package user;
    option go_package = "github.com/example/proto/user";

    service UserService {
      // Unary RPC - single request, single response
      rpc GetUser(GetUserRequest) returns (GetUserResponse);
      rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
      rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);

      // Server streaming - single request, stream of responses
      rpc ListUsers(ListUsersRequest) returns (stream User);

      // Client streaming - stream of requests, single response
      rpc UploadUsers(stream User) returns (UploadUsersResponse);

      // Bidirectional streaming - both sides stream
      rpc Chat(stream ChatMessage) returns (stream ChatMessage);
    }

    message GetUserRequest {
      int32 id = 1;
    }

    message GetUserResponse {
      User user = 1;
    }

    message CreateUserRequest {
      string name = 1;
      string email = 2;
    }

    message CreateUserResponse {
      User user = 1;
    }

    message DeleteUserRequest {
      int32 id = 1;
    }

    message DeleteUserResponse {
      bool success = 1;
      string message = 2;
    }

    message ListUsersRequest {
      int32 limit = 1;
    }

    message UploadUsersResponse {
      int32 count = 1;
    }

    message User {
      int32 id = 1;
      string name = 2;
      string email = 3;
    }

    message ChatMessage {
      string user = 1;
      string text = 2;
    }
```

## RPC Types
```
rpc_types:
  unary:
    description: Client sends one request, server sends one response
    pattern: "rpc GetUser(Request) returns (Response)"
    use_case: Standard request-response (like REST endpoints)
    analogy: Regular function call

  server_streaming:
    description: Client sends one request, server sends stream of responses
    pattern: "rpc ListUsers(Request) returns (stream Response)"
    use_case: Large result sets, real-time feeds, file download
    analogy: Server-Sent Events

  client_streaming:
    description: Client sends stream of requests, server sends one response
    pattern: "rpc UploadUsers(stream Request) returns (Response)"
    use_case: File upload, batch operations, aggregation
    analogy: Uploading chunks

  bidirectional_streaming:
    description: Both client and server send streams independently
    pattern: "rpc Chat(stream Request) returns (stream Response)"
    use_case: Chat, real-time collaboration, gaming
    analogy: WebSocket
```

## Code Generation
```
code_generation:
  tool: protoc (Protocol Buffer Compiler)

  install_protoc:
    macos: "brew install protobuf"
    linux: "apt install -y protobuf-compiler"

  go_plugins:
    install: |
      go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
      go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

  generate_go:
    command: |
      protoc --go_out=. --go_opt=paths=source_relative \
             --go-grpc_out=. --go-grpc_opt=paths=source_relative \
             proto/user.proto
    generates:
      - "user.pb.go - Message types and serialization"
      - "user_grpc.pb.go - Client stub and server interface"
```

## Interceptors
```
interceptors:
  description: Middleware for gRPC (like HTTP middleware)
  types:
    unary_interceptor: "For unary RPCs"
    stream_interceptor: "For streaming RPCs"

  use_cases:
    - Logging
    - Authentication/Authorization
    - Rate limiting
    - Metrics collection
    - Error handling
    - Request validation

  chaining: "Multiple interceptors can be chained (executed in order)"
```

## Deadlines and Cancellation
```
deadlines:
  description: Client sets a deadline for how long it will wait for a response
  behavior:
    - If deadline expires, client gets DEADLINE_EXCEEDED error
    - Server should check deadline and stop processing if expired
    - Deadline propagates across service calls (service A -> B -> C)

  best_practice:
    - Always set deadlines on client calls
    - Check deadline in long-running server handlers
    - Propagate context (carries deadline) to downstream calls

  grpc_status_codes:
    OK: "0 - Success"
    CANCELLED: "1 - Client cancelled"
    UNKNOWN: "2 - Unknown error"
    INVALID_ARGUMENT: "3 - Bad request"
    DEADLINE_EXCEEDED: "4 - Deadline expired"
    NOT_FOUND: "5 - Resource not found"
    ALREADY_EXISTS: "6 - Duplicate"
    PERMISSION_DENIED: "7 - Forbidden"
    RESOURCE_EXHAUSTED: "8 - Rate limited"
    UNAUTHENTICATED: "16 - No valid credentials"
    UNIMPLEMENTED: "12 - Method not implemented"
    INTERNAL: "13 - Internal server error"
    UNAVAILABLE: "14 - Service unavailable"
```

## gRPC vs REST
```
comparison:
  protocol:
    grpc: "HTTP/2 (binary framing, multiplexing)"
    rest: "HTTP/1.1 or HTTP/2 (text-based)"

  serialization:
    grpc: "Protocol Buffers (binary, compact)"
    rest: "JSON (text, human-readable)"

  contract:
    grpc: "Strict .proto file (code generation)"
    rest: "Optional OpenAPI/Swagger spec"

  streaming:
    grpc: "Native bidirectional streaming"
    rest: "Limited (SSE for server-push, WebSocket is separate)"

  browser_support:
    grpc: "Not native (needs gRPC-Web proxy)"
    rest: "Native (fetch, XMLHttpRequest)"

  performance:
    grpc: "5-10x faster serialization, smaller payloads"
    rest: "Slower but good enough for most use cases"

  tooling:
    grpc: "grpcurl, grpcui, Postman (limited)"
    rest: "curl, Postman, browser, any HTTP tool"

  when_to_use_grpc:
    - Microservice-to-microservice communication
    - Low-latency, high-throughput internal APIs
    - Streaming data (real-time feeds, file transfer)
    - Polyglot environments (generate clients for any language)

  when_to_use_rest:
    - Public-facing APIs
    - Browser clients
    - Simple CRUD operations
    - When human readability matters
```

## Code Examples

### Proto File
```
proto_file: |
  // proto/user.proto
  syntax = "proto3";

  package user;
  option go_package = "github.com/example/grpc-demo/proto/user";

  service UserService {
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
    rpc ListUsers(ListUsersRequest) returns (stream User);
  }

  message GetUserRequest {
    int32 id = 1;
  }

  message GetUserResponse {
    User user = 1;
  }

  message CreateUserRequest {
    string name = 1;
    string email = 2;
  }

  message CreateUserResponse {
    User user = 1;
  }

  message ListUsersRequest {
    int32 limit = 1;
  }

  message User {
    int32 id = 1;
    string name = 2;
    string email = 3;
  }
```

### gRPC Server in Go
```go
package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"sync"
	"time"

	pb "github.com/example/grpc-demo/proto/user"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type server struct {
	pb.UnimplementedUserServiceServer
	mu     sync.RWMutex
	users  map[int32]*pb.User
	nextID int32
}

func newServer() *server {
	return &server{
		users:  make(map[int32]*pb.User),
		nextID: 1,
	}
}

// Unary RPC - Get a single user
func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
	// Check if deadline exceeded
	if ctx.Err() == context.DeadlineExceeded {
		return nil, status.Error(codes.DeadlineExceeded, "deadline exceeded")
	}

	s.mu.RLock()
	user, ok := s.users[req.Id]
	s.mu.RUnlock()

	if !ok {
		return nil, status.Errorf(codes.NotFound, "user %d not found", req.Id)
	}

	return &pb.GetUserResponse{User: user}, nil
}

// Unary RPC - Create a user
func (s *server) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	if req.Name == "" || req.Email == "" {
		return nil, status.Error(codes.InvalidArgument, "name and email are required")
	}

	s.mu.Lock()
	user := &pb.User{
		Id:    s.nextID,
		Name:  req.Name,
		Email: req.Email,
	}
	s.users[s.nextID] = user
	s.nextID++
	s.mu.Unlock()

	return &pb.CreateUserResponse{User: user}, nil
}

// Server streaming RPC - List users one by one
func (s *server) ListUsers(req *pb.ListUsersRequest, stream pb.UserService_ListUsersServer) error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	count := int32(0)
	for _, user := range s.users {
		if req.Limit > 0 && count >= req.Limit {
			break
		}

		if err := stream.Send(user); err != nil {
			return status.Errorf(codes.Internal, "error sending user: %v", err)
		}
		count++
		time.Sleep(100 * time.Millisecond) // simulate delay
	}

	return nil
}

// Logging interceptor (middleware)
func loggingInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {
	start := time.Now()
	resp, err := handler(ctx, req)
	duration := time.Since(start)

	st, _ := status.FromError(err)
	log.Printf("method=%s duration=%s status=%s", info.FullMethod, duration, st.Code())

	return resp, err
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(loggingInterceptor),
	)

	srv := newServer()

	// Seed some data
	srv.users[1] = &pb.User{Id: 1, Name: "Ankit", Email: "ankit@example.com"}
	srv.users[2] = &pb.User{Id: 2, Name: "Priya", Email: "priya@example.com"}
	srv.nextID = 3

	pb.RegisterUserServiceServer(grpcServer, srv)

	fmt.Println("gRPC server running on :50051")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
```

### gRPC Client in Go
```go
package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	pb "github.com/example/grpc-demo/proto/user"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
)

func main() {
	// Connect to server
	conn, err := grpc.NewClient("localhost:50051",
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("failed to connect: %v", err)
	}
	defer conn.Close()

	client := pb.NewUserServiceClient(conn)

	// Set deadline (timeout)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Create a user
	createResp, err := client.CreateUser(ctx, &pb.CreateUserRequest{
		Name:  "Rahul",
		Email: "rahul@example.com",
	})
	if err != nil {
		st, _ := status.FromError(err)
		log.Fatalf("CreateUser failed: %s - %s", st.Code(), st.Message())
	}
	fmt.Printf("Created user: %+v\n", createResp.User)

	// Get a user
	getResp, err := client.GetUser(ctx, &pb.GetUserRequest{Id: 1})
	if err != nil {
		st, _ := status.FromError(err)
		log.Fatalf("GetUser failed: %s - %s", st.Code(), st.Message())
	}
	fmt.Printf("Got user: %+v\n", getResp.User)

	// List users (server streaming)
	stream, err := client.ListUsers(ctx, &pb.ListUsersRequest{Limit: 10})
	if err != nil {
		log.Fatalf("ListUsers failed: %v", err)
	}

	fmt.Println("All users:")
	for {
		user, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatalf("stream error: %v", err)
		}
		fmt.Printf("  - %s (%s)\n", user.Name, user.Email)
	}
}
```
