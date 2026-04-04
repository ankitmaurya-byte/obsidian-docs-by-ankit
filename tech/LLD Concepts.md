# LLD Concepts

## What is Low Level Design
```
overview:
  definition: Detailed design of individual components, classes, interfaces, and their interactions
  focus: How to implement a system at the code level
  contrast_with_hld:
    high_level_design: What components exist and how they communicate (databases, services, queues)
    low_level_design: How each component is internally structured (classes, methods, relationships)
  interview_focus:
    - Identify entities and their attributes
    - Define relationships between entities
    - Apply appropriate design patterns
    - Write clean, extensible code
    - Handle concurrency and edge cases
```

## OOP Principles

### Encapsulation
```
encapsulation:
  what: Bundle data and methods that operate on that data within a single unit, restricting direct access
  why:
    - Protect internal state from invalid modifications
    - Hide implementation details from consumers
    - Change internals without breaking external code
  go_approach: Exported (uppercase) vs unexported (lowercase) fields and methods
```

```go
package main

import (
    "errors"
    "fmt"
)

// BankAccount encapsulates balance — no direct access
type BankAccount struct {
    owner   string  // unexported: only accessible within this package
    balance float64 // unexported: can't set negative balance directly
}

func NewBankAccount(owner string, initial float64) (*BankAccount, error) {
    if initial < 0 {
        return nil, errors.New("initial balance cannot be negative")
    }
    return &BankAccount{owner: owner, balance: initial}, nil
}

func (a *BankAccount) Deposit(amount float64) error {
    if amount <= 0 {
        return errors.New("deposit must be positive")
    }
    a.balance += amount
    return nil
}

func (a *BankAccount) Withdraw(amount float64) error {
    if amount <= 0 {
        return errors.New("withdrawal must be positive")
    }
    if amount > a.balance {
        return errors.New("insufficient funds")
    }
    a.balance -= amount
    return nil
}

func (a *BankAccount) Balance() float64 {
    return a.balance
}

func main() {
    acc, _ := NewBankAccount("Ankit", 1000)
    acc.Deposit(500)
    acc.Withdraw(200)
    fmt.Printf("Balance: %.2f\n", acc.Balance()) // 1300.00
    // acc.balance = -9999  // NOT possible from outside the package
}
```

### Inheritance (Embedding in Go)
```
inheritance:
  what: A mechanism where one type acquires the properties and behaviors of another
  classic_oop: Child class extends parent class
  go_approach: Go has NO inheritance — uses struct embedding (composition) instead
  embedding:
    - Embed a struct inside another struct
    - Promoted methods — embedded struct's methods are accessible on outer struct
    - NOT "is-a" relationship, it's "has-a" with syntactic sugar
  why_go_avoids_inheritance:
    - Avoids deep hierarchy problems
    - Encourages composition over inheritance
    - Simpler mental model
```

```go
package main

import "fmt"

// Base struct
type Animal struct {
    Name string
    Age  int
}

func (a *Animal) Eat() {
    fmt.Printf("%s is eating\n", a.Name)
}

func (a *Animal) Sleep() {
    fmt.Printf("%s is sleeping\n", a.Name)
}

// Dog embeds Animal — gets all Animal methods promoted
type Dog struct {
    Animal       // embedding, not inheritance
    Breed string
}

func (d *Dog) Bark() {
    fmt.Printf("%s says Woof!\n", d.Name) // Name promoted from Animal
}

// Can override promoted methods
func (d *Dog) Eat() {
    fmt.Printf("%s is eating dog food\n", d.Name)
}

func main() {
    dog := &Dog{
        Animal: Animal{Name: "Rex", Age: 3},
        Breed:  "German Shepherd",
    }
    dog.Eat()   // calls Dog.Eat (overridden)
    dog.Sleep() // calls Animal.Sleep (promoted)
    dog.Bark()  // calls Dog.Bark

    // Access embedded struct directly
    dog.Animal.Eat() // calls Animal.Eat explicitly
}
```

### Polymorphism
```
polymorphism:
  what: Same interface, different underlying behavior depending on the concrete type
  classic_oop: Method overriding via virtual functions
  go_approach: Interfaces — any type that implements the methods satisfies the interface
  types:
    compile_time: Not applicable in Go (no method overloading)
    runtime: Interface-based dispatch — concrete type determined at runtime
  power: Write code that works with any type implementing an interface
```

```go
package main

import (
    "fmt"
    "math"
)

// Interface defines behavior contract
type Shape interface {
    Area() float64
    Perimeter() float64
}

type Circle struct {
    Radius float64
}

func (c *Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c *Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

type Rectangle struct {
    Width, Height float64
}

func (r *Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r *Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

// Works with ANY Shape — polymorphism
func PrintShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}

func TotalArea(shapes []Shape) float64 {
    total := 0.0
    for _, s := range shapes {
        total += s.Area()
    }
    return total
}

func main() {
    shapes := []Shape{
        &Circle{Radius: 5},
        &Rectangle{Width: 4, Height: 6},
        &Circle{Radius: 3},
    }

    for _, s := range shapes {
        PrintShapeInfo(s) // different behavior for each concrete type
    }

    fmt.Printf("Total area: %.2f\n", TotalArea(shapes))
}
```

### Abstraction
```
abstraction:
  what: Hide complex implementation details, expose only what is necessary
  why:
    - Reduce complexity for the caller
    - Define clear contracts
    - Swap implementations without changing consumers
  go_approach: Interfaces define WHAT, structs define HOW
  guideline: Accept interfaces, return structs
```

```go
package main

import "fmt"

// Abstraction — caller only knows about this interface
type MessageQueue interface {
    Publish(topic string, msg []byte) error
    Subscribe(topic string, handler func([]byte)) error
}

// Implementation 1 — Kafka
type KafkaQueue struct {
    brokers []string
}

func (k *KafkaQueue) Publish(topic string, msg []byte) error {
    fmt.Printf("[Kafka] Publishing to %s: %s\n", topic, msg)
    return nil
}

func (k *KafkaQueue) Subscribe(topic string, handler func([]byte)) error {
    fmt.Printf("[Kafka] Subscribed to %s\n", topic)
    handler([]byte("kafka message"))
    return nil
}

// Implementation 2 — RabbitMQ
type RabbitQueue struct {
    url string
}

func (r *RabbitQueue) Publish(topic string, msg []byte) error {
    fmt.Printf("[RabbitMQ] Publishing to %s: %s\n", topic, msg)
    return nil
}

func (r *RabbitQueue) Subscribe(topic string, handler func([]byte)) error {
    fmt.Printf("[RabbitMQ] Subscribed to %s\n", topic)
    handler([]byte("rabbit message"))
    return nil
}

// Service only depends on the abstraction
type OrderService struct {
    queue MessageQueue // depends on interface, not concrete type
}

func (o *OrderService) PlaceOrder(orderID string) {
    o.queue.Publish("orders", []byte(orderID))
}

func main() {
    // Swap implementation without changing OrderService
    service := &OrderService{queue: &KafkaQueue{brokers: []string{"localhost:9092"}}}
    service.PlaceOrder("ORD-001")

    service2 := &OrderService{queue: &RabbitQueue{url: "amqp://localhost"}}
    service2.PlaceOrder("ORD-002")
}
```

## SOLID Principles

### Single Responsibility Principle (SRP)
```
srp:
  what: A struct/type should have only one reason to change
  violation: A struct that handles user validation, database saving, AND email sending
  fix: Split into UserValidator, UserRepository, EmailService
  benefit: Changes to email logic don't affect database logic
```

### Open/Closed Principle (OCP)
```
ocp:
  what: Open for extension, closed for modification
  violation: Adding a new payment type requires modifying existing ProcessPayment function
  fix: Define PaymentMethod interface, add new types without touching existing code
  go_approach: New struct implementing existing interface = extension without modification
```

### Liskov Substitution Principle (LSP)
```
lsp:
  what: Subtypes must be substitutable for their base types without altering correctness
  violation: Square overriding Rectangle.SetWidth in a way that breaks area calculation
  fix: If substitution breaks behavior, the hierarchy is wrong — redesign
  go_approach: If a type implements an interface, it must fulfill the full contract
```

### Interface Segregation Principle (ISP)
```
isp:
  what: No client should be forced to depend on methods it does not use
  violation: One large interface with 10 methods when most callers need only 2
  fix: Split into small, focused interfaces
  go_idiom: Go interfaces are naturally small — io.Reader has 1 method, io.Writer has 1 method
```

```go
package main

import "fmt"

// BAD: fat interface — forces implementors to add methods they don't need
type Animal interface {
    Walk()
    Swim()
    Fly()
}

// GOOD: small focused interfaces
type Walker interface {
    Walk()
}

type Swimmer interface {
    Swim()
}

type Flyer interface {
    Fly()
}

// Duck implements all three
type Duck struct{}
func (d *Duck) Walk() { fmt.Println("Duck walking") }
func (d *Duck) Swim() { fmt.Println("Duck swimming") }
func (d *Duck) Fly()  { fmt.Println("Duck flying") }

// Dog only implements Walker and Swimmer — not forced to implement Fly
type Dog struct{}
func (d *Dog) Walk() { fmt.Println("Dog walking") }
func (d *Dog) Swim() { fmt.Println("Dog swimming") }

// Functions accept only what they need
func MakeItWalk(w Walker) { w.Walk() }
func MakeItSwim(s Swimmer) { s.Swim() }

func main() {
    duck := &Duck{}
    dog := &Dog{}

    MakeItWalk(duck)
    MakeItWalk(dog)
    MakeItSwim(duck)
    MakeItSwim(dog)
}
```

### Dependency Inversion Principle (DIP)
```
dip:
  what: High-level modules should not depend on low-level modules — both should depend on abstractions
  violation: OrderService directly creates MySQLDatabase inside itself
  fix: OrderService depends on a Repository interface, concrete DB is injected
  go_approach: Accept interfaces as constructor/function parameters
```

## Key Design Principles

### DRY, KISS, YAGNI
```
dry:
  what: Don't Repeat Yourself
  meaning: Every piece of knowledge should have a single, unambiguous representation
  violation: Same validation logic copy-pasted in 5 handlers
  fix: Extract into a shared function or middleware

kiss:
  what: Keep It Simple, Stupid
  meaning: Prefer the simplest solution that works
  violation: Using a complex design pattern when a simple function would suffice
  fix: Start simple, refactor when complexity is actually needed

yagni:
  what: You Aren't Gonna Need It
  meaning: Don't build features or abstractions until they are actually required
  violation: Adding a plugin system "just in case" when there's only one implementation
  fix: Build what you need now, extend later
```

### Composition Over Inheritance
```
composition_over_inheritance:
  what: Prefer composing objects from smaller pieces rather than building deep inheritance hierarchies
  why:
    - Inheritance creates tight coupling between parent and child
    - Deep hierarchies are hard to understand and modify
    - Go doesn't have inheritance — composition is the only option
    - More flexible — swap behaviors at runtime
  how_in_go:
    - Embed structs for code reuse
    - Use interfaces for polymorphism
    - Pass dependencies as fields (inject behavior)
```

```go
package main

import "fmt"

// Instead of: HTTPServer inherits from TCPServer inherits from Server
// Compose behaviors:

type Logger interface {
    Log(msg string)
}

type ConsoleLogger struct{}
func (c *ConsoleLogger) Log(msg string) { fmt.Println("[LOG]", msg) }

type Authenticator interface {
    Authenticate(token string) bool
}

type JWTAuth struct{}
func (j *JWTAuth) Authenticate(token string) bool {
    return token == "valid-token"
}

type RateLimiter interface {
    Allow(ip string) bool
}

type TokenBucket struct{}
func (t *TokenBucket) Allow(ip string) bool { return true }

// Server is composed of behaviors — not inherited from a chain
type Server struct {
    logger Logger
    auth   Authenticator
    limiter RateLimiter
}

func NewServer(l Logger, a Authenticator, r RateLimiter) *Server {
    return &Server{logger: l, auth: a, limiter: r}
}

func (s *Server) HandleRequest(token, ip, body string) {
    s.logger.Log("Incoming request from " + ip)
    if !s.limiter.Allow(ip) {
        s.logger.Log("Rate limited")
        return
    }
    if !s.auth.Authenticate(token) {
        s.logger.Log("Unauthorized")
        return
    }
    s.logger.Log("Processing: " + body)
}

func main() {
    server := NewServer(&ConsoleLogger{}, &JWTAuth{}, &TokenBucket{})
    server.HandleRequest("valid-token", "192.168.1.1", "hello")
}
```

### Dependency Injection
```
dependency_injection:
  what: Pass dependencies to a component rather than letting it create them internally
  types:
    constructor_injection: Pass via NewXxx() function (most common in Go)
    method_injection: Pass via method parameters
    field_injection: Set struct fields directly (less common)
  benefits:
    - Easy to test (inject mocks)
    - Loose coupling
    - Swap implementations at runtime
  go_approach: Accept interfaces in constructors, pass concrete types at the call site
```

```go
package main

import "fmt"

// Dependency defined as interface
type EmailSender interface {
    Send(to, subject, body string) error
}

// Real implementation
type SMTPSender struct {
    host string
}

func (s *SMTPSender) Send(to, subject, body string) error {
    fmt.Printf("SMTP sending to %s: %s\n", to, subject)
    return nil
}

// Mock for testing
type MockSender struct {
    Calls []string
}

func (m *MockSender) Send(to, subject, body string) error {
    m.Calls = append(m.Calls, to)
    return nil
}

// Service accepts dependency via constructor injection
type UserService struct {
    emailer EmailSender
}

func NewUserService(emailer EmailSender) *UserService {
    return &UserService{emailer: emailer}
}

func (u *UserService) Register(email string) {
    fmt.Printf("Registering user: %s\n", email)
    u.emailer.Send(email, "Welcome!", "Thanks for signing up")
}

func main() {
    // Production: inject real sender
    realService := NewUserService(&SMTPSender{host: "smtp.gmail.com"})
    realService.Register("ankit@example.com")

    // Testing: inject mock
    mock := &MockSender{}
    testService := NewUserService(mock)
    testService.Register("test@example.com")
    fmt.Printf("Mock recorded %d calls\n", len(mock.Calls))
}
```

### Coupling vs Cohesion
```
coupling:
  what: Degree of interdependence between modules
  tight_coupling:
    - Module A directly creates and uses Module B's concrete types
    - Change in B forces change in A
    - Hard to test in isolation
  loose_coupling:
    - Module A depends on an interface, not concrete type
    - Modules communicate through well-defined contracts
    - Easy to swap, test, and modify independently
  goal: MINIMIZE coupling

cohesion:
  what: Degree to which elements within a module belong together
  low_cohesion:
    - A single struct handles user auth, email sending, AND logging
    - Methods are unrelated to each other
  high_cohesion:
    - AuthService only handles authentication
    - All methods relate to the same responsibility
  goal: MAXIMIZE cohesion

summary: Low coupling + High cohesion = Good design
```

### Law of Demeter
```
law_of_demeter:
  what: A method should only call methods on its immediate dependencies (don't talk to strangers)
  also_called: Principle of Least Knowledge
  violation: order.GetCustomer().GetAddress().GetCity()  # train wreck
  fix: order.GetShippingCity()  # encapsulate the traversal
  rule_of_thumb: Only use one dot — a.B() is fine, a.B().C() is suspicious
```

### Tell Don't Ask
```
tell_dont_ask:
  what: Tell objects what to do, don't ask for their state and make decisions for them
  violation: |
    if account.GetBalance() >= amount {
        account.SetBalance(account.GetBalance() - amount)
    }
  fix: |
    account.Withdraw(amount)  // let the object handle its own logic
  benefit: Logic stays with the data, enforces encapsulation
```

## How to Approach LLD Interviews
```
lld_interview_approach:
  step_1_clarify_requirements:
    - Ask what the system should do (use cases)
    - Ask about scale (single machine? concurrent users?)
    - Identify core features vs nice-to-have
    - Ask about edge cases

  step_2_identify_entities:
    - List all nouns from requirements — these become classes/structs
    - Identify attributes for each entity
    - Example (parking lot): ParkingLot, Floor, ParkingSpot, Vehicle, Ticket, Payment

  step_3_define_relationships:
    - has-a: ParkingLot has many Floors
    - uses: Ticket references a ParkingSpot
    - implements: Car, Bike implement Vehicle interface
    - relationship_types:
        one_to_one: Ticket to ParkingSpot (at a given time)
        one_to_many: Floor to ParkingSpots
        many_to_many: (rare in LLD, usually broken into junction)

  step_4_identify_interfaces:
    - Find common behaviors across types
    - Define contracts (what, not how)
    - Keep interfaces small (ISP)

  step_5_apply_patterns:
    - Factory: when you need to create different subtypes
    - Strategy: when algorithms need to be swappable
    - Observer: when state changes need notifications
    - State: when object behavior changes based on state
    - Singleton: when exactly one instance is needed

  step_6_write_code:
    - Start with interfaces and struct definitions
    - Implement core business logic
    - Handle edge cases and error conditions
    - Make it thread-safe if required

  common_mistakes:
    - Over-engineering with patterns that aren't needed (YAGNI)
    - Starting to code before understanding requirements
    - Ignoring concurrency in multi-user systems
    - Making everything public/exported
    - Deep coupling between entities
```

```
class_diagram_template:
  entities:
    EntityName:
      attributes:
        - fieldName: type
      methods:
        - MethodName(params): returnType
      relationships:
        - has_many: OtherEntity
        - implements: InterfaceName

  interfaces:
    InterfaceName:
      methods:
        - MethodName(params): returnType

  patterns_used:
    - pattern_name: where_applied
```
