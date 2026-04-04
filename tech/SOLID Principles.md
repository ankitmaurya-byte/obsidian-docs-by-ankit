# SOLID Principles

## What are SOLID Principles
```
overview:
  definition: Five design principles that make software more maintainable, flexible, and scalable
  coined_by: Robert C. Martin (Uncle Bob)
  principles:
    S: Single Responsibility Principle
    O: Open/Closed Principle
    L: Liskov Substitution Principle
    I: Interface Segregation Principle
    D: Dependency Inversion Principle
  goal: Write code that is easy to change, test, and extend
```

## Single Responsibility Principle (SRP)
```
single_responsibility:
  definition: A struct/module should have only one reason to change
  meaning: Each type should do one thing and do it well
  real_world_analogy: >
    A chef cooks food, a waiter serves food, a cashier handles payment.
    If one person did all three, changing the payment system would require
    retraining someone who also cooks, risking mistakes in the kitchen.

  why_it_matters:
    - Easier to understand (smaller, focused types)
    - Easier to test (fewer dependencies)
    - Changes in one area don't break another
    - Better code reuse
```

### Bad Example
```go
// BAD: User struct does too many things
type User struct {
    Name  string
    Email string
}

// This struct handles business logic AND persistence AND notifications
func (u *User) Save() error {
    // Validate user
    if u.Name == "" {
        return fmt.Errorf("name required")
    }

    // Save to database (persistence concern)
    db, _ := sql.Open("postgres", "connection_string")
    _, err := db.Exec("INSERT INTO users (name, email) VALUES ($1, $2)", u.Name, u.Email)
    if err != nil {
        return err
    }

    // Send welcome email (notification concern)
    smtp.SendMail("smtp.gmail.com:587", auth, "from@app.com",
        []string{u.Email}, []byte("Welcome!"))

    return nil
}
```

### Good Example
```go
// GOOD: Each type has one responsibility

// Domain model - only holds data and validation
type User struct {
    Name  string
    Email string
}

func (u *User) Validate() error {
    if u.Name == "" {
        return fmt.Errorf("name required")
    }
    if u.Email == "" {
        return fmt.Errorf("email required")
    }
    return nil
}

// Repository - only handles persistence
type UserRepository struct {
    db *sql.DB
}

func (r *UserRepository) Save(u *User) error {
    _, err := r.db.Exec("INSERT INTO users (name, email) VALUES ($1, $2)", u.Name, u.Email)
    return err
}

func (r *UserRepository) FindByEmail(email string) (*User, error) {
    // ... query logic
    return nil, nil
}

// Notifier - only handles notifications
type EmailNotifier struct {
    smtpHost string
}

func (n *EmailNotifier) SendWelcome(u *User) error {
    // ... send email logic
    return nil
}

// Service - orchestrates the workflow
type UserService struct {
    repo     *UserRepository
    notifier *EmailNotifier
}

func (s *UserService) Register(u *User) error {
    if err := u.Validate(); err != nil {
        return err
    }
    if err := s.repo.Save(u); err != nil {
        return err
    }
    return s.notifier.SendWelcome(u)
}
```

## Open/Closed Principle (OCP)
```
open_closed:
  definition: Software entities should be open for extension, but closed for modification
  meaning: Add new behavior by writing new code, not changing existing code
  real_world_analogy: >
    A power strip is closed for modification (you don't rewire it to add a new outlet),
    but open for extension (you plug in any device that fits the socket interface).

  why_it_matters:
    - Existing tested code stays untouched
    - New features don't introduce bugs in old features
    - Follows the "plug-in" architecture philosophy
```

### Bad Example
```go
// BAD: Adding a new payment method requires modifying existing function
func CalculateDiscount(customerType string, amount float64) float64 {
    switch customerType {
    case "regular":
        return amount * 0.05
    case "premium":
        return amount * 0.10
    case "vip":
        return amount * 0.20
    // Every new customer type = modify this function
    // case "enterprise": return amount * 0.25
    default:
        return 0
    }
}
```

### Good Example
```go
// GOOD: New discount strategies without changing existing code

type DiscountStrategy interface {
    Calculate(amount float64) float64
}

type RegularDiscount struct{}
func (d *RegularDiscount) Calculate(amount float64) float64 {
    return amount * 0.05
}

type PremiumDiscount struct{}
func (d *PremiumDiscount) Calculate(amount float64) float64 {
    return amount * 0.10
}

type VIPDiscount struct{}
func (d *VIPDiscount) Calculate(amount float64) float64 {
    return amount * 0.20
}

// Adding a new type requires ZERO changes to existing code
type EnterpriseDiscount struct{}
func (d *EnterpriseDiscount) Calculate(amount float64) float64 {
    return amount * 0.25
}

// This function never needs to change
func ApplyDiscount(strategy DiscountStrategy, amount float64) float64 {
    return strategy.Calculate(amount)
}

// Usage
func main() {
    amount := 100.0
    fmt.Println(ApplyDiscount(&VIPDiscount{}, amount))        // 20
    fmt.Println(ApplyDiscount(&EnterpriseDiscount{}, amount)) // 25
}
```

## Liskov Substitution Principle (LSP)
```
liskov_substitution:
  definition: >
    Subtypes must be substitutable for their base types without altering
    the correctness of the program
  meaning: If code works with an interface, it should work with ANY implementation of that interface
  real_world_analogy: >
    If you hire a driver, any licensed driver should work. You should not have to
    check if it's specifically a taxi driver vs a bus driver - any "driver" should
    be able to drive your car without breaking it.

  why_it_matters:
    - Polymorphism actually works correctly
    - Prevents subtle bugs from bad implementations
    - Code using interfaces can trust the contract

  violations_to_watch:
    - Implementation throws unexpected errors
    - Implementation ignores parameters
    - Implementation has side effects the interface doesn't promise
    - Implementation only partially works
```

### Bad Example
```go
// BAD: Square violates the Rectangle contract
type Rectangle struct {
    Width  float64
    Height float64
}

func (r *Rectangle) SetWidth(w float64)  { r.Width = w }
func (r *Rectangle) SetHeight(h float64) { r.Height = h }
func (r *Rectangle) Area() float64       { return r.Width * r.Height }

type Square struct {
    Rectangle
}

// Violates LSP: setting width also changes height
// Code that expects a Rectangle will get wrong results
func (s *Square) SetWidth(w float64) {
    s.Width = w
    s.Height = w // surprise side effect!
}

func (s *Square) SetHeight(h float64) {
    s.Width = h  // surprise side effect!
    s.Height = h
}

// This function breaks with Square
func DoubleWidth(r *Rectangle) float64 {
    r.SetWidth(r.Width * 2)
    // Expects: Area = (2 * width) * height
    // With Square: Area = (2 * width) * (2 * width) -- WRONG
    return r.Area()
}
```

### Good Example
```go
// GOOD: Use interfaces that define behavior, not inheritance

type Shape interface {
    Area() float64
    Perimeter() float64
}

type Rectangle struct {
    Width  float64
    Height float64
}

func (r Rectangle) Area() float64      { return r.Width * r.Height }
func (r Rectangle) Perimeter() float64 { return 2 * (r.Width + r.Height) }

type Square struct {
    Side float64
}

func (s Square) Area() float64      { return s.Side * s.Side }
func (s Square) Perimeter() float64 { return 4 * s.Side }

// Works correctly with ANY Shape implementation
func PrintShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}

// Another LSP-compliant example: storage
type Storage interface {
    Save(key string, data []byte) error
    Load(key string) ([]byte, error)
}

type FileStorage struct{ basePath string }
func (f *FileStorage) Save(key string, data []byte) error {
    return os.WriteFile(filepath.Join(f.basePath, key), data, 0644)
}
func (f *FileStorage) Load(key string) ([]byte, error) {
    return os.ReadFile(filepath.Join(f.basePath, key))
}

type S3Storage struct{ bucket string }
func (s *S3Storage) Save(key string, data []byte) error { /* S3 put */ return nil }
func (s *S3Storage) Load(key string) ([]byte, error)    { /* S3 get */ return nil, nil }

// Both work identically wherever Storage is expected
func BackupData(store Storage, key string, data []byte) error {
    return store.Save(key, data)
}
```

## Interface Segregation Principle (ISP)
```
interface_segregation:
  definition: No client should be forced to depend on methods it does not use
  meaning: Prefer many small, focused interfaces over one large interface
  real_world_analogy: >
    A Swiss Army knife has 20 tools, but if you just need to cut paper,
    you only want scissors. Don't force someone to carry the whole knife
    when they only need one tool.

  why_it_matters:
    - Reduces coupling (depend only on what you use)
    - Easier to implement (fewer methods to satisfy)
    - Easier to mock in tests
    - More composable

  go_philosophy: >
    Go's standard library follows this naturally.
    io.Reader has 1 method. io.Writer has 1 method.
    io.ReadWriter composes both. This is ISP in action.
```

### Bad Example
```go
// BAD: One fat interface forces implementations to have methods they don't need
type Animal interface {
    Walk()
    Swim()
    Fly()
    Speak()
}

// Dog can walk and speak, but forced to implement Swim and Fly
type Dog struct{}
func (d Dog) Walk()  { fmt.Println("Dog walks") }
func (d Dog) Swim()  { panic("dogs don't swim well") } // forced empty/bad implementation
func (d Dog) Fly()   { panic("dogs can't fly") }       // violates the contract
func (d Dog) Speak() { fmt.Println("Woof") }

// Fish can swim but forced to implement Walk, Fly, Speak
type Fish struct{}
func (f Fish) Walk()  { panic("fish can't walk") }
func (f Fish) Swim()  { fmt.Println("Fish swims") }
func (f Fish) Fly()   { panic("fish can't fly") }
func (f Fish) Speak() { panic("fish can't speak") }
```

### Good Example
```go
// GOOD: Small, focused interfaces
type Walker interface {
    Walk()
}

type Swimmer interface {
    Swim()
}

type Flyer interface {
    Fly()
}

type Speaker interface {
    Speak()
}

// Dog implements only what it can do
type Dog struct{}
func (d Dog) Walk()  { fmt.Println("Dog walks") }
func (d Dog) Speak() { fmt.Println("Woof") }

// Fish implements only what it can do
type Fish struct{}
func (f Fish) Swim() { fmt.Println("Fish swims") }

// Duck implements multiple interfaces (composition)
type Duck struct{}
func (d Duck) Walk()  { fmt.Println("Duck walks") }
func (d Duck) Swim()  { fmt.Println("Duck swims") }
func (d Duck) Fly()   { fmt.Println("Duck flies") }
func (d Duck) Speak() { fmt.Println("Quack") }

// Functions accept only what they need
func MakeItWalk(w Walker)  { w.Walk() }
func MakeItSwim(s Swimmer) { s.Swim() }

// Compose interfaces when needed
type AquaticBird interface {
    Walker
    Swimmer
    Flyer
}

// Real-world Go example: io package
// io.Reader  = just Read()
// io.Writer  = just Write()
// io.Closer  = just Close()
// io.ReadWriter     = Read() + Write()
// io.ReadWriteCloser = Read() + Write() + Close()
```

## Dependency Inversion Principle (DIP)
```
dependency_inversion:
  definition: >
    High-level modules should not depend on low-level modules.
    Both should depend on abstractions (interfaces).
    Abstractions should not depend on details.
    Details should depend on abstractions.
  meaning: Depend on interfaces, not concrete implementations
  real_world_analogy: >
    A wall socket defines the interface (shape, voltage). Any appliance that
    matches the socket works. The house wiring (high-level) doesn't depend
    on specific appliances (low-level). Both depend on the socket standard (abstraction).

  why_it_matters:
    - Swap implementations easily (test doubles, different databases)
    - High-level business logic is protected from infrastructure changes
    - Enables dependency injection
    - Makes testing trivial
```

### Bad Example
```go
// BAD: High-level OrderService directly depends on low-level MySQLDatabase
type MySQLDatabase struct{}

func (db *MySQLDatabase) SaveOrder(order Order) error {
    // MySQL-specific code
    return nil
}

type OrderService struct {
    db *MySQLDatabase // directly depends on MySQL - can't swap to Postgres
}

func (s *OrderService) PlaceOrder(order Order) error {
    // Business logic...
    return s.db.SaveOrder(order) // tightly coupled to MySQL
}

// To switch to PostgreSQL, you have to:
// 1. Change OrderService struct
// 2. Change everywhere OrderService is created
// 3. Can't easily test without a real MySQL database
```

### Good Example
```go
// GOOD: Depend on abstractions (interfaces)

// Abstraction - defined by the consumer (Go convention)
type OrderRepository interface {
    Save(order Order) error
    FindByID(id string) (*Order, error)
}

// High-level module depends on interface
type OrderService struct {
    repo     OrderRepository
    notifier Notifier
}

func NewOrderService(repo OrderRepository, notifier Notifier) *OrderService {
    return &OrderService{repo: repo, notifier: notifier}
}

func (s *OrderService) PlaceOrder(order Order) error {
    if err := order.Validate(); err != nil {
        return err
    }
    if err := s.repo.Save(order); err != nil {
        return err
    }
    return s.notifier.Notify(order.CustomerEmail, "Order placed!")
}

// Low-level module implements the interface
type MySQLOrderRepo struct {
    db *sql.DB
}

func (r *MySQLOrderRepo) Save(order Order) error {
    _, err := r.db.Exec("INSERT INTO orders ...")
    return err
}

func (r *MySQLOrderRepo) FindByID(id string) (*Order, error) {
    // ... MySQL query
    return nil, nil
}

// Can easily swap to a different implementation
type PostgresOrderRepo struct {
    db *sql.DB
}

func (r *PostgresOrderRepo) Save(order Order) error {
    // ... Postgres query
    return nil
}

func (r *PostgresOrderRepo) FindByID(id string) (*Order, error) {
    // ... Postgres query
    return nil, nil
}

// Easy to test with a mock
type MockOrderRepo struct {
    orders map[string]Order
}

func (m *MockOrderRepo) Save(order Order) error {
    m.orders[order.ID] = order
    return nil
}

func (m *MockOrderRepo) FindByID(id string) (*Order, error) {
    order, ok := m.orders[id]
    if !ok {
        return nil, fmt.Errorf("not found")
    }
    return &order, nil
}

// Wire everything together in main
func main() {
    // Production
    db, _ := sql.Open("postgres", "connection_string")
    repo := &PostgresOrderRepo{db: db}
    notifier := &EmailNotifier{host: "smtp.gmail.com"}
    service := NewOrderService(repo, notifier)

    // Test
    mockRepo := &MockOrderRepo{orders: make(map[string]Order)}
    mockNotifier := &MockNotifier{}
    testService := NewOrderService(mockRepo, mockNotifier)
    _ = testService
    _ = service
}
```

## SOLID Summary
```
summary:
  S_single_responsibility:
    rule: One struct, one job
    check: "Does this type have more than one reason to change?"
    fix: Split into smaller, focused types

  O_open_closed:
    rule: Extend behavior without modifying existing code
    check: "Do I need to edit existing code to add a new feature?"
    fix: Use interfaces and polymorphism

  L_liskov_substitution:
    rule: Any implementation should work wherever the interface is used
    check: "Can I swap implementations without breaking things?"
    fix: Don't add surprising side effects, honor the contract

  I_interface_segregation:
    rule: Small, focused interfaces over large ones
    check: "Do implementations need to stub out methods they don't use?"
    fix: Break large interfaces into smaller ones

  D_dependency_inversion:
    rule: Depend on interfaces, not concrete types
    check: "Can I easily swap the database/notifier/logger?"
    fix: Accept interfaces, return structs

  go_idioms:
    - Accept interfaces, return structs
    - Define interfaces where they are used (consumer side)
    - Keep interfaces small (1-3 methods)
    - Use constructor functions for dependency injection
    - Embed interfaces for composition
```
