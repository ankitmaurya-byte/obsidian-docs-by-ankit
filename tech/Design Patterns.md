# Design Patterns

## What are Design Patterns
```
overview:
  definition: Reusable solutions to common software design problems
  origin: "Gang of Four (GoF) book - Design Patterns: Elements of Reusable Object-Oriented Software"
  categories:
    creational: How objects are created
    structural: How objects are composed/structured
    behavioral: How objects communicate and interact
  important_note: Go is not a classic OOP language, patterns are adapted using interfaces, structs, and functions
```

## Creational Patterns

### Singleton
```
singleton:
  what: Ensure a class has only one instance and provide global access to it
  when_to_use:
    - Database connection pool
    - Logger
    - Configuration manager
    - Cache instance
  when_to_avoid:
    - Makes unit testing harder (hidden dependency)
    - Can become a god object
    - Tight coupling
  go_approach: Use sync.Once for thread-safe lazy initialization
```

```go
package main

import (
    "fmt"
    "sync"
)

// Singleton using sync.Once (thread-safe)
type Database struct {
    connection string
}

var (
    dbInstance *Database
    dbOnce     sync.Once
)

func GetDatabase() *Database {
    dbOnce.Do(func() {
        fmt.Println("Creating database connection...")
        dbInstance = &Database{connection: "postgres://localhost:5432/mydb"}
    })
    return dbInstance
}

func main() {
    db1 := GetDatabase() // prints "Creating database connection..."
    db2 := GetDatabase() // does NOT print again
    fmt.Println(db1 == db2) // true - same instance
}
```

### Factory
```
factory:
  what: Create objects without specifying the exact type, delegate to a factory function
  when_to_use:
    - Object creation logic is complex
    - Need to create different types based on input
    - Want to decouple creation from usage
    - Creating objects that implement a common interface
  variants:
    simple_factory: Single function that returns different types
    factory_method: Interface defines creation, subtypes implement it
    abstract_factory: Family of related objects
```

```go
package main

import "fmt"

// Common interface
type Notifier interface {
    Send(message string) error
}

// Concrete implementations
type EmailNotifier struct{}
func (e *EmailNotifier) Send(message string) error {
    fmt.Println("Email:", message)
    return nil
}

type SMSNotifier struct{}
func (s *SMSNotifier) Send(message string) error {
    fmt.Println("SMS:", message)
    return nil
}

type SlackNotifier struct{}
func (s *SlackNotifier) Send(message string) error {
    fmt.Println("Slack:", message)
    return nil
}

// Factory function
func NewNotifier(notifierType string) (Notifier, error) {
    switch notifierType {
    case "email":
        return &EmailNotifier{}, nil
    case "sms":
        return &SMSNotifier{}, nil
    case "slack":
        return &SlackNotifier{}, nil
    default:
        return nil, fmt.Errorf("unknown notifier type: %s", notifierType)
    }
}

// Factory with functional options (more idiomatic Go)
type ServerConfig struct {
    Host    string
    Port    int
    TLS     bool
    Timeout int
}

type ServerOption func(*ServerConfig)

func WithPort(port int) ServerOption {
    return func(c *ServerConfig) { c.Port = port }
}

func WithTLS() ServerOption {
    return func(c *ServerConfig) { c.TLS = true }
}

func WithTimeout(seconds int) ServerOption {
    return func(c *ServerConfig) { c.Timeout = seconds }
}

func NewServer(host string, opts ...ServerOption) *ServerConfig {
    config := &ServerConfig{
        Host:    host,
        Port:    8080,  // default
        Timeout: 30,    // default
    }
    for _, opt := range opts {
        opt(config)
    }
    return config
}

func main() {
    notifier, _ := NewNotifier("email")
    notifier.Send("Hello from factory!")

    server := NewServer("localhost", WithPort(9090), WithTLS())
    fmt.Printf("Server: %+v\n", server)
}
```

### Builder
```
builder:
  what: Construct complex objects step by step, separating construction from representation
  when_to_use:
    - Object has many optional parameters
    - Construction involves multiple steps
    - Want to create different representations of the same object
  go_approach: Functional options pattern (above) or method chaining
```

```go
package main

import "fmt"

// Builder with method chaining
type QueryBuilder struct {
    table      string
    conditions []string
    orderBy    string
    limit      int
    offset     int
}

func NewQueryBuilder(table string) *QueryBuilder {
    return &QueryBuilder{table: table, limit: -1}
}

func (qb *QueryBuilder) Where(condition string) *QueryBuilder {
    qb.conditions = append(qb.conditions, condition)
    return qb
}

func (qb *QueryBuilder) OrderBy(field string) *QueryBuilder {
    qb.orderBy = field
    return qb
}

func (qb *QueryBuilder) Limit(n int) *QueryBuilder {
    qb.limit = n
    return qb
}

func (qb *QueryBuilder) Offset(n int) *QueryBuilder {
    qb.offset = n
    return qb
}

func (qb *QueryBuilder) Build() string {
    query := "SELECT * FROM " + qb.table
    for i, cond := range qb.conditions {
        if i == 0 {
            query += " WHERE " + cond
        } else {
            query += " AND " + cond
        }
    }
    if qb.orderBy != "" {
        query += " ORDER BY " + qb.orderBy
    }
    if qb.limit > 0 {
        query += fmt.Sprintf(" LIMIT %d", qb.limit)
    }
    if qb.offset > 0 {
        query += fmt.Sprintf(" OFFSET %d", qb.offset)
    }
    return query
}

func main() {
    query := NewQueryBuilder("users").
        Where("age > 18").
        Where("active = true").
        OrderBy("created_at DESC").
        Limit(10).
        Offset(20).
        Build()
    fmt.Println(query)
    // SELECT * FROM users WHERE age > 18 AND active = true ORDER BY created_at DESC LIMIT 10 OFFSET 20
}
```

## Structural Patterns

### Adapter
```
adapter:
  what: Convert interface of one type to another that a client expects
  analogy: Power plug adapter - converts one plug shape to another
  when_to_use:
    - Integrating third-party libraries with different interfaces
    - Legacy code that can't be modified
    - Making incompatible interfaces work together
```

```go
package main

import "fmt"

// Existing interface your code expects
type PaymentProcessor interface {
    Pay(amount float64) error
}

// Third-party library with different interface
type StripeAPI struct{}
func (s *StripeAPI) MakeCharge(amountCents int, currency string) error {
    fmt.Printf("Stripe charging %d cents %s\n", amountCents, currency)
    return nil
}

// Adapter - wraps Stripe to match PaymentProcessor interface
type StripeAdapter struct {
    stripe   *StripeAPI
    currency string
}

func NewStripeAdapter(currency string) *StripeAdapter {
    return &StripeAdapter{
        stripe:   &StripeAPI{},
        currency: currency,
    }
}

func (sa *StripeAdapter) Pay(amount float64) error {
    cents := int(amount * 100)
    return sa.stripe.MakeCharge(cents, sa.currency)
}

func main() {
    var processor PaymentProcessor = NewStripeAdapter("USD")
    processor.Pay(29.99) // Stripe charging 2999 cents USD
}
```

### Decorator
```
decorator:
  what: Add behavior to an object dynamically without modifying its structure
  analogy: Adding toppings to a pizza - each topping wraps the base
  when_to_use:
    - Add logging, caching, auth to existing functions
    - HTTP middleware
    - Extend behavior without subclassing
  go_approach: Function wrapping or interface wrapping
```

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "time"
)

// HTTP middleware is the classic decorator in Go
type Middleware func(http.HandlerFunc) http.HandlerFunc

// Logging decorator
func withLogging(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    }
}

// Auth decorator
func withAuth(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next(w, r)
    }
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "Hello, World!")
}

// Interface-based decorator
type DataStore interface {
    Get(key string) (string, error)
    Set(key, value string) error
}

type SimpleStore struct {
    data map[string]string
}

func (s *SimpleStore) Get(key string) (string, error) {
    v, ok := s.data[key]
    if !ok {
        return "", fmt.Errorf("key not found")
    }
    return v, nil
}

func (s *SimpleStore) Set(key, value string) error {
    s.data[key] = value
    return nil
}

// LoggingStore decorates any DataStore with logging
type LoggingStore struct {
    inner DataStore
}

func (ls *LoggingStore) Get(key string) (string, error) {
    log.Printf("GET %s", key)
    return ls.inner.Get(key)
}

func (ls *LoggingStore) Set(key, value string) error {
    log.Printf("SET %s = %s", key, value)
    return ls.inner.Set(key, value)
}

func main() {
    // Stack decorators: auth first, then logging
    http.HandleFunc("/hello", withLogging(withAuth(helloHandler)))

    // Interface decorator
    var store DataStore = &LoggingStore{
        inner: &SimpleStore{data: make(map[string]string)},
    }
    store.Set("name", "ankit")
    store.Get("name")
}
```

### Proxy
```
proxy:
  what: Provide a surrogate or placeholder that controls access to another object
  types:
    protection_proxy: Controls access based on permissions
    virtual_proxy: Lazy initialization, create expensive object only when needed
    caching_proxy: Cache results of expensive operations
    logging_proxy: Log all operations
  when_to_use:
    - Lazy loading of expensive resources
    - Access control / authorization
    - Caching
    - Rate limiting
```

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Database interface {
    Query(sql string) string
}

// Real database (expensive to create/call)
type RealDatabase struct{}

func (db *RealDatabase) Query(sql string) string {
    time.Sleep(100 * time.Millisecond) // simulate slow query
    return fmt.Sprintf("Result for: %s", sql)
}

// Caching proxy
type CachingProxy struct {
    db    Database
    cache map[string]string
    mu    sync.RWMutex
}

func NewCachingProxy(db Database) *CachingProxy {
    return &CachingProxy{
        db:    db,
        cache: make(map[string]string),
    }
}

func (cp *CachingProxy) Query(sql string) string {
    cp.mu.RLock()
    if result, ok := cp.cache[sql]; ok {
        cp.mu.RUnlock()
        fmt.Println("Cache hit!")
        return result
    }
    cp.mu.RUnlock()

    result := cp.db.Query(sql)

    cp.mu.Lock()
    cp.cache[sql] = result
    cp.mu.Unlock()

    return result
}

func main() {
    db := NewCachingProxy(&RealDatabase{})
    fmt.Println(db.Query("SELECT * FROM users")) // slow
    fmt.Println(db.Query("SELECT * FROM users")) // fast - cache hit
}
```

### Facade
```
facade:
  what: Provide a simplified interface to a complex subsystem
  analogy: Car ignition - one key turn starts engine, fuel pump, electrical, etc.
  when_to_use:
    - Simplify interaction with complex libraries
    - Decouple client from subsystem implementation
    - Provide a clean API over messy internals
    - Microservice orchestration
```

```go
package main

import "fmt"

// Complex subsystems
type UserService struct{}
func (u *UserService) GetUser(id int) string { return fmt.Sprintf("User-%d", id) }

type PaymentService struct{}
func (p *PaymentService) Charge(userId string, amount float64) bool {
    fmt.Printf("Charging %s: $%.2f\n", userId, amount)
    return true
}

type InventoryService struct{}
func (i *InventoryService) Reserve(productId string) bool {
    fmt.Printf("Reserving %s\n", productId)
    return true
}

type NotificationService struct{}
func (n *NotificationService) SendEmail(to, msg string) {
    fmt.Printf("Email to %s: %s\n", to, msg)
}

// Facade - simple interface over complex subsystems
type OrderFacade struct {
    users     *UserService
    payments  *PaymentService
    inventory *InventoryService
    notifier  *NotificationService
}

func NewOrderFacade() *OrderFacade {
    return &OrderFacade{
        users:     &UserService{},
        payments:  &PaymentService{},
        inventory: &InventoryService{},
        notifier:  &NotificationService{},
    }
}

// One simple method hides all the complexity
func (f *OrderFacade) PlaceOrder(userId int, productId string, amount float64) error {
    user := f.users.GetUser(userId)
    if !f.inventory.Reserve(productId) {
        return fmt.Errorf("product not available")
    }
    if !f.payments.Charge(user, amount) {
        return fmt.Errorf("payment failed")
    }
    f.notifier.SendEmail(user, "Order confirmed!")
    return nil
}

func main() {
    facade := NewOrderFacade()
    facade.PlaceOrder(1, "PROD-123", 49.99)
}
```

## Behavioral Patterns

### Observer
```
observer:
  what: Define a one-to-many dependency so when one object changes state, all dependents are notified
  also_called: Pub/Sub, Event-Driven
  when_to_use:
    - Event systems
    - UI updates when data changes
    - Notification systems
    - Decoupled communication between components
```

```go
package main

import "fmt"

// Observer interface
type EventHandler func(data interface{})

// Event emitter (Subject/Observable)
type EventEmitter struct {
    listeners map[string][]EventHandler
}

func NewEventEmitter() *EventEmitter {
    return &EventEmitter{listeners: make(map[string][]EventHandler)}
}

func (e *EventEmitter) On(event string, handler EventHandler) {
    e.listeners[event] = append(e.listeners[event], handler)
}

func (e *EventEmitter) Emit(event string, data interface{}) {
    for _, handler := range e.listeners[event] {
        handler(data)
    }
}

// Usage
type OrderEvent struct {
    OrderID string
    Amount  float64
}

func main() {
    emitter := NewEventEmitter()

    // Register observers
    emitter.On("order.created", func(data interface{}) {
        order := data.(OrderEvent)
        fmt.Printf("Send confirmation email for order %s\n", order.OrderID)
    })

    emitter.On("order.created", func(data interface{}) {
        order := data.(OrderEvent)
        fmt.Printf("Update inventory for order %s\n", order.OrderID)
    })

    emitter.On("order.created", func(data interface{}) {
        order := data.(OrderEvent)
        fmt.Printf("Process payment $%.2f for order %s\n", order.Amount, order.OrderID)
    })

    // Emit event - all observers are notified
    emitter.Emit("order.created", OrderEvent{OrderID: "ORD-123", Amount: 49.99})
}
```

### Strategy
```
strategy:
  what: Define a family of algorithms, encapsulate each one, and make them interchangeable
  when_to_use:
    - Multiple algorithms for the same task
    - Want to switch algorithm at runtime
    - Avoid large if/else or switch blocks
    - Payment processing, compression, sorting strategies
  go_approach: Use interfaces or function types
```

```go
package main

import "fmt"

// Strategy as interface
type CompressionStrategy interface {
    Compress(data []byte) []byte
}

type GzipCompression struct{}
func (g *GzipCompression) Compress(data []byte) []byte {
    fmt.Println("Compressing with gzip...")
    return data // simplified
}

type ZipCompression struct{}
func (z *ZipCompression) Compress(data []byte) []byte {
    fmt.Println("Compressing with zip...")
    return data
}

// Context that uses the strategy
type FileCompressor struct {
    strategy CompressionStrategy
}

func (fc *FileCompressor) SetStrategy(s CompressionStrategy) {
    fc.strategy = s
}

func (fc *FileCompressor) CompressFile(data []byte) []byte {
    return fc.strategy.Compress(data)
}

// Strategy as function type (more idiomatic Go)
type SortFunc func([]int) []int

func WithBubbleSort(arr []int) []int {
    fmt.Println("Using bubble sort")
    // ... sorting logic
    return arr
}

func WithQuickSort(arr []int) []int {
    fmt.Println("Using quick sort")
    // ... sorting logic
    return arr
}

func SortData(data []int, strategy SortFunc) []int {
    return strategy(data)
}

func main() {
    compressor := &FileCompressor{strategy: &GzipCompression{}}
    compressor.CompressFile([]byte("data"))

    compressor.SetStrategy(&ZipCompression{})
    compressor.CompressFile([]byte("data"))

    // Function-based strategy
    data := []int{3, 1, 2}
    SortData(data, WithQuickSort)
}
```

### Command
```
command:
  what: Encapsulate a request as an object, allowing parameterization, queuing, and undo
  when_to_use:
    - Undo/redo functionality
    - Transaction logging
    - Task queuing
    - Macro recording
    - Decouple sender from receiver
```

```go
package main

import "fmt"

// Command interface
type Command interface {
    Execute()
    Undo()
}

// Concrete commands
type AddTextCommand struct {
    editor *TextEditor
    text   string
}

func (c *AddTextCommand) Execute() {
    c.editor.content += c.text
}

func (c *AddTextCommand) Undo() {
    c.editor.content = c.editor.content[:len(c.editor.content)-len(c.text)]
}

// Receiver
type TextEditor struct {
    content string
}

// Invoker with undo support
type CommandHistory struct {
    history []Command
}

func (ch *CommandHistory) Execute(cmd Command) {
    cmd.Execute()
    ch.history = append(ch.history, cmd)
}

func (ch *CommandHistory) Undo() {
    if len(ch.history) == 0 {
        return
    }
    last := ch.history[len(ch.history)-1]
    last.Undo()
    ch.history = ch.history[:len(ch.history)-1]
}

func main() {
    editor := &TextEditor{}
    history := &CommandHistory{}

    history.Execute(&AddTextCommand{editor: editor, text: "Hello "})
    history.Execute(&AddTextCommand{editor: editor, text: "World"})
    fmt.Println(editor.content) // "Hello World"

    history.Undo()
    fmt.Println(editor.content) // "Hello "

    history.Undo()
    fmt.Println(editor.content) // ""
}
```

### Iterator
```
iterator:
  what: Provide a way to access elements of a collection sequentially without exposing internals
  when_to_use:
    - Traverse custom data structures
    - Need multiple traversal strategies
    - Hide internal representation
  go_approach: Go uses channels and range, or Next()/HasNext() pattern
```

```go
package main

import "fmt"

// Iterator pattern using Next/Value
type TreeNode struct {
    Val   int
    Left  *TreeNode
    Right *TreeNode
}

type BSTIterator struct {
    stack []*TreeNode
}

func NewBSTIterator(root *TreeNode) *BSTIterator {
    it := &BSTIterator{}
    it.pushLeft(root)
    return it
}

func (it *BSTIterator) pushLeft(node *TreeNode) {
    for node != nil {
        it.stack = append(it.stack, node)
        node = node.Left
    }
}

func (it *BSTIterator) HasNext() bool {
    return len(it.stack) > 0
}

func (it *BSTIterator) Next() int {
    node := it.stack[len(it.stack)-1]
    it.stack = it.stack[:len(it.stack)-1]
    it.pushLeft(node.Right)
    return node.Val
}

// Iterator using channels (Go-idiomatic)
func inOrderChannel(root *TreeNode) <-chan int {
    ch := make(chan int)
    go func() {
        defer close(ch)
        var walk func(*TreeNode)
        walk = func(node *TreeNode) {
            if node == nil {
                return
            }
            walk(node.Left)
            ch <- node.Val
            walk(node.Right)
        }
        walk(root)
    }()
    return ch
}

func main() {
    //       4
    //      / \
    //     2   6
    //    / \
    //   1   3
    root := &TreeNode{Val: 4,
        Left: &TreeNode{Val: 2,
            Left:  &TreeNode{Val: 1},
            Right: &TreeNode{Val: 3},
        },
        Right: &TreeNode{Val: 6},
    }

    // Next/HasNext style
    it := NewBSTIterator(root)
    for it.HasNext() {
        fmt.Print(it.Next(), " ") // 1 2 3 4 6
    }
    fmt.Println()

    // Channel style
    for val := range inOrderChannel(root) {
        fmt.Print(val, " ") // 1 2 3 4 6
    }
}
```

## Pattern Selection Guide
```
when_to_use_which:
  need_single_instance:           Singleton
  need_object_creation_logic:     Factory
  need_complex_object_step_by_step: Builder
  need_interface_conversion:      Adapter
  need_add_behavior_dynamically:  Decorator
  need_control_access:            Proxy
  need_simplify_complex_system:   Facade
  need_event_notification:        Observer
  need_swap_algorithms:           Strategy
  need_undo_redo:                 Command
  need_traverse_collection:       Iterator

go_specific_notes:
  - Prefer interfaces over abstract classes (Go has no classes)
  - Functional options pattern replaces Builder in many cases
  - Function types can replace Strategy and Command
  - Channels naturally implement Observer pattern
  - Middleware pattern is Go's idiomatic Decorator
  - Embedding replaces inheritance-based patterns
```
