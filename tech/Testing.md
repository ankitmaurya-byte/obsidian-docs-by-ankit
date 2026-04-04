# Testing

## What is Testing
```
overview:
  definition: Process of verifying that software works correctly and meets requirements
  why_it_matters:
    - Catches bugs before production
    - Enables confident refactoring
    - Documents expected behavior
    - Reduces debugging time
    - Prevents regressions

  test_pyramid:
    top_few:        "E2E Tests (slow, expensive, brittle)"
    middle_some:    "Integration Tests (moderate speed, test connections)"
    bottom_many:    "Unit Tests (fast, cheap, isolated)"
    principle: >
      Write many unit tests, fewer integration tests, even fewer E2E tests.
      Lower levels are faster, cheaper, and more stable.
```

## Unit Testing
```
unit_testing:
  what: Test individual functions/methods in isolation
  characteristics:
    - Fast (milliseconds)
    - No external dependencies (DB, API, filesystem)
    - Tests one thing at a time
    - Dependencies are mocked/stubbed
    - Deterministic (same result every time)

  what_to_test:
    - Pure functions (input -> output)
    - Business logic
    - Edge cases and boundary conditions
    - Error handling
    - Validation logic

  what_not_to_test:
    - Simple getters/setters (no logic)
    - Third-party library internals
    - Implementation details (test behavior, not structure)
```

### Go Unit Testing
```go
// calculator.go
package calculator

import "fmt"

func Add(a, b int) int {
    return a + b
}

func Divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

func IsPrime(n int) bool {
    if n < 2 {
        return false
    }
    for i := 2; i*i <= n; i++ {
        if n%i == 0 {
            return false
        }
    }
    return true
}
```

```go
// calculator_test.go
package calculator

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}

func TestDivide(t *testing.T) {
    result, err := Divide(10, 2)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if result != 5.0 {
        t.Errorf("Divide(10, 2) = %f; want 5.0", result)
    }
}

func TestDivideByZero(t *testing.T) {
    _, err := Divide(10, 0)
    if err == nil {
        t.Fatal("expected error for division by zero, got nil")
    }
}

// Subtests for grouping related tests
func TestIsPrime(t *testing.T) {
    t.Run("prime numbers", func(t *testing.T) {
        primes := []int{2, 3, 5, 7, 11, 13}
        for _, n := range primes {
            if !IsPrime(n) {
                t.Errorf("IsPrime(%d) = false; want true", n)
            }
        }
    })

    t.Run("non-prime numbers", func(t *testing.T) {
        nonPrimes := []int{0, 1, 4, 6, 8, 9, 10}
        for _, n := range nonPrimes {
            if IsPrime(n) {
                t.Errorf("IsPrime(%d) = true; want false", n)
            }
        }
    })
}
```

## Table-Driven Tests
```
table_driven:
  what: Define test cases as a table (slice of structs), loop through them
  why:
    - Reduces boilerplate
    - Easy to add new test cases
    - All cases visible in one place
    - Go community convention
  pattern:
    1: Define struct with input and expected output
    2: Create slice of test cases
    3: Loop and run each as a subtest with t.Run
```

```go
package calculator

import "testing"

func TestAddTableDriven(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -2, -3},
        {"zero", 0, 0, 0},
        {"mixed", -1, 5, 4},
        {"large numbers", 1000000, 2000000, 3000000},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

func TestDivideTableDriven(t *testing.T) {
    tests := []struct {
        name      string
        a, b      float64
        expected  float64
        expectErr bool
    }{
        {"normal division", 10, 2, 5.0, false},
        {"decimal result", 7, 2, 3.5, false},
        {"divide by zero", 10, 0, 0, true},
        {"zero numerator", 0, 5, 0, false},
        {"negative division", -10, 2, -5.0, false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.a, tt.b)
            if tt.expectErr {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if result != tt.expected {
                t.Errorf("Divide(%f, %f) = %f; want %f", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

## Integration Testing
```
integration_testing:
  what: Test how multiple components work together
  tests_the_boundaries:
    - Application + database
    - Application + external API
    - Service A + Service B
    - Handler + service + repository

  characteristics:
    - Slower than unit tests
    - May need real or containerized dependencies
    - Test the wiring between components
    - May use test databases, testcontainers

  go_approach:
    - Use build tags to separate from unit tests
    - Use TestMain for setup/teardown
    - Use testcontainers-go for Docker dependencies
```

```go
// integration_test.go
//go:build integration

package repository

import (
    "context"
    "database/sql"
    "testing"

    _ "github.com/lib/pq"
)

var testDB *sql.DB

// TestMain runs once before all tests in the package
func TestMain(m *testing.M) {
    var err error
    testDB, err = sql.Open("postgres", "postgres://localhost:5432/testdb?sslmode=disable")
    if err != nil {
        panic(err)
    }
    defer testDB.Close()

    // Setup: create tables
    testDB.Exec(`CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )`)

    // Run tests
    code := m.Run()

    // Teardown: clean up
    testDB.Exec("DROP TABLE IF EXISTS users")
    os.Exit(code)
}

func TestUserRepository_SaveAndFind(t *testing.T) {
    // Clean state for this test
    testDB.Exec("DELETE FROM users")

    repo := NewUserRepository(testDB)
    ctx := context.Background()

    // Save
    user := &User{Name: "Ankit", Email: "ankit@test.com"}
    err := repo.Save(ctx, user)
    if err != nil {
        t.Fatalf("Save failed: %v", err)
    }

    // Find
    found, err := repo.FindByEmail(ctx, "ankit@test.com")
    if err != nil {
        t.Fatalf("FindByEmail failed: %v", err)
    }

    if found.Name != "Ankit" {
        t.Errorf("Name = %s; want Ankit", found.Name)
    }
}

// Run with: go test -tags=integration -v ./...
```

## End-to-End (E2E) Testing
```
e2e_testing:
  what: Test the entire application from the user's perspective
  tests_the_full_flow:
    - "User signs up -> gets email -> logs in -> creates order"
    - HTTP request -> API -> database -> response

  characteristics:
    - Slowest test type
    - Most brittle (depends on everything working)
    - Highest confidence (tests real behavior)
    - Expensive to maintain

  go_approach:
    - Use httptest.NewServer for HTTP tests
    - Spin up real dependencies with Docker
    - Test actual HTTP endpoints

  js_tools:
    - Cypress (browser-based)
    - Playwright (browser-based)
    - Supertest (HTTP API testing)
```

```go
package main

import (
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"
)

func TestCreateUserE2E(t *testing.T) {
    // Setup: create the full application server
    app := SetupApp() // returns http.Handler with all routes wired
    server := httptest.NewServer(app)
    defer server.Close()

    // Create user
    body := `{"name": "Ankit", "email": "ankit@test.com"}`
    resp, err := http.Post(server.URL+"/api/users", "application/json",
        strings.NewReader(body))
    if err != nil {
        t.Fatalf("POST /api/users failed: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusCreated {
        t.Fatalf("status = %d; want 201", resp.StatusCode)
    }

    // Verify response
    var user struct {
        ID    int    `json:"id"`
        Name  string `json:"name"`
        Email string `json:"email"`
    }
    json.NewDecoder(resp.Body).Decode(&user)

    if user.Name != "Ankit" {
        t.Errorf("Name = %s; want Ankit", user.Name)
    }

    // Verify user can be fetched
    resp2, err := http.Get(server.URL + "/api/users/" + "ankit@test.com")
    if err != nil {
        t.Fatalf("GET /api/users failed: %v", err)
    }
    defer resp2.Body.Close()

    if resp2.StatusCode != http.StatusOK {
        t.Fatalf("GET status = %d; want 200", resp2.StatusCode)
    }
}
```

## Test-Driven Development (TDD)
```
tdd:
  what: Write tests BEFORE writing the implementation code
  cycle:
    red: Write a failing test
    green: Write minimum code to make the test pass
    refactor: Clean up the code while keeping tests green

  benefits:
    - Forces you to think about API design first
    - Tests are always written (not skipped)
    - Code is testable by design
    - Documentation through tests
    - Small, focused iterations

  when_to_use:
    - Business logic with clear requirements
    - Bug fixes (write test that reproduces bug first)
    - Library/API design

  when_to_skip:
    - Prototyping / exploring
    - UI code that changes frequently
    - Simple CRUD with no logic
```

```go
// TDD Example: build a stack step by step

// Step 1 (RED): Write failing test
func TestStack_IsEmptyOnNew(t *testing.T) {
    s := NewStack()
    if !s.IsEmpty() {
        t.Error("new stack should be empty")
    }
}

// Step 2 (GREEN): Minimum implementation
type Stack struct {
    items []int
}

func NewStack() *Stack         { return &Stack{} }
func (s *Stack) IsEmpty() bool { return len(s.items) == 0 }

// Step 3 (RED): Next test
func TestStack_PushAndPop(t *testing.T) {
    s := NewStack()
    s.Push(42)
    val, ok := s.Pop()
    if !ok || val != 42 {
        t.Errorf("Pop() = %d, %v; want 42, true", val, ok)
    }
}

// Step 4 (GREEN): Implement Push and Pop
func (s *Stack) Push(val int) { s.items = append(s.items, val) }
func (s *Stack) Pop() (int, bool) {
    if s.IsEmpty() {
        return 0, false
    }
    val := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return val, true
}

// Step 5 (RED): Edge case test
func TestStack_PopEmpty(t *testing.T) {
    s := NewStack()
    _, ok := s.Pop()
    if ok {
        t.Error("Pop on empty stack should return false")
    }
}
// Already passes! Refactor if needed, then move on.
```

## Mocking
```
mocking:
  what: Replace real dependencies with fake implementations for testing
  why:
    - Isolate the unit under test
    - Control dependency behavior (return specific values, errors)
    - Avoid slow/flaky external calls
    - Test error handling paths

  go_approach:
    - Define interfaces for dependencies
    - Create mock structs that implement the interface
    - No framework needed (but testify/mock and gomock exist)

  when_to_mock:
    - External APIs (HTTP calls)
    - Databases
    - File system
    - Time-dependent code
    - Anything slow or non-deterministic

  when_NOT_to_mock:
    - Simple value objects
    - Pure functions
    - The thing you are testing
    - Too many mocks = test is testing mocks, not code
```

```go
// service.go
package order

type OrderRepository interface {
    Save(order *Order) error
    FindByID(id string) (*Order, error)
}

type PaymentGateway interface {
    Charge(amount float64, currency string) (string, error)
}

type Notifier interface {
    Send(to, message string) error
}

type OrderService struct {
    repo     OrderRepository
    payment  PaymentGateway
    notifier Notifier
}

func NewOrderService(repo OrderRepository, payment PaymentGateway, notifier Notifier) *OrderService {
    return &OrderService{repo: repo, payment: payment, notifier: notifier}
}

func (s *OrderService) PlaceOrder(order *Order) error {
    txnID, err := s.payment.Charge(order.Total, "USD")
    if err != nil {
        return fmt.Errorf("payment failed: %w", err)
    }
    order.TransactionID = txnID
    order.Status = "confirmed"

    if err := s.repo.Save(order); err != nil {
        return fmt.Errorf("save failed: %w", err)
    }

    s.notifier.Send(order.CustomerEmail, "Order confirmed!")
    return nil
}
```

```go
// service_test.go
package order

import (
    "fmt"
    "testing"
)

// Mock implementations
type MockOrderRepo struct {
    orders    map[string]*Order
    saveError error
}

func (m *MockOrderRepo) Save(order *Order) error {
    if m.saveError != nil {
        return m.saveError
    }
    m.orders[order.ID] = order
    return nil
}

func (m *MockOrderRepo) FindByID(id string) (*Order, error) {
    order, ok := m.orders[id]
    if !ok {
        return nil, fmt.Errorf("not found")
    }
    return order, nil
}

type MockPaymentGateway struct {
    chargeError error
    txnID       string
}

func (m *MockPaymentGateway) Charge(amount float64, currency string) (string, error) {
    if m.chargeError != nil {
        return "", m.chargeError
    }
    return m.txnID, nil
}

type MockNotifier struct {
    sent []string
}

func (m *MockNotifier) Send(to, message string) error {
    m.sent = append(m.sent, to+": "+message)
    return nil
}

// Tests
func TestPlaceOrder_Success(t *testing.T) {
    repo := &MockOrderRepo{orders: make(map[string]*Order)}
    payment := &MockPaymentGateway{txnID: "txn-123"}
    notifier := &MockNotifier{}

    service := NewOrderService(repo, payment, notifier)

    order := &Order{ID: "ord-1", Total: 99.99, CustomerEmail: "test@test.com"}
    err := service.PlaceOrder(order)

    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if order.Status != "confirmed" {
        t.Errorf("status = %s; want confirmed", order.Status)
    }
    if order.TransactionID != "txn-123" {
        t.Errorf("txnID = %s; want txn-123", order.TransactionID)
    }
    if len(notifier.sent) != 1 {
        t.Errorf("expected 1 notification, got %d", len(notifier.sent))
    }
}

func TestPlaceOrder_PaymentFails(t *testing.T) {
    repo := &MockOrderRepo{orders: make(map[string]*Order)}
    payment := &MockPaymentGateway{chargeError: fmt.Errorf("card declined")}
    notifier := &MockNotifier{}

    service := NewOrderService(repo, payment, notifier)

    order := &Order{ID: "ord-1", Total: 99.99}
    err := service.PlaceOrder(order)

    if err == nil {
        t.Fatal("expected error, got nil")
    }
    if len(repo.orders) != 0 {
        t.Error("order should not be saved when payment fails")
    }
}

func TestPlaceOrder_SaveFails(t *testing.T) {
    repo := &MockOrderRepo{orders: make(map[string]*Order), saveError: fmt.Errorf("db down")}
    payment := &MockPaymentGateway{txnID: "txn-123"}
    notifier := &MockNotifier{}

    service := NewOrderService(repo, payment, notifier)

    order := &Order{ID: "ord-1", Total: 99.99}
    err := service.PlaceOrder(order)

    if err == nil {
        t.Fatal("expected error, got nil")
    }
}
```

## Test Coverage
```
test_coverage:
  what: Percentage of code executed during tests
  go_commands:
    run_with_coverage: "go test -cover ./..."
    generate_report: "go test -coverprofile=coverage.out ./..."
    view_html_report: "go tool cover -html=coverage.out"
    view_by_function: "go tool cover -func=coverage.out"

  guidelines:
    target: "70-80% for business logic is good"
    100_percent: "Not always practical or useful"
    what_matters: "Cover critical paths, edge cases, error handling"
    low_value: "Don't chase coverage on trivial code"

  what_coverage_misses:
    - Code runs but logic is wrong (need assertions)
    - Missing test cases for edge inputs
    - Concurrency bugs
    - Integration issues
```

## Benchmarking
```
benchmarking:
  what: Measure performance of code (how fast, how much memory)
  go_approach:
    - Functions named BenchmarkXxx(b *testing.B)
    - Run with: go test -bench=. -benchmem
    - b.N is auto-adjusted by the framework

  commands:
    run_all: "go test -bench=. -benchmem ./..."
    run_specific: "go test -bench=BenchmarkFib -benchmem"
    compare: "go test -bench=. -count=5 | benchstat"
    cpu_profile: "go test -bench=. -cpuprofile=cpu.out"
    mem_profile: "go test -bench=. -memprofile=mem.out"
```

```go
package calculator

import "testing"

func BenchmarkIsPrime(b *testing.B) {
    for i := 0; i < b.N; i++ {
        IsPrime(7919) // test with a known prime
    }
}

// Benchmark with different inputs
func BenchmarkIsPrimeTable(b *testing.B) {
    cases := []struct {
        name string
        n    int
    }{
        {"small", 7},
        {"medium", 7919},
        {"large", 999983},
    }

    for _, tc := range cases {
        b.Run(tc.name, func(b *testing.B) {
            for i := 0; i < b.N; i++ {
                IsPrime(tc.n)
            }
        })
    }
}

// Benchmark comparing implementations
func BenchmarkFibMemo(b *testing.B) {
    for i := 0; i < b.N; i++ {
        memo := make(map[int]int)
        fibMemo(30, memo)
    }
}

func BenchmarkFibTab(b *testing.B) {
    for i := 0; i < b.N; i++ {
        fibTab(30)
    }
}

// Output example:
// BenchmarkIsPrime-8      50000000    25.3 ns/op    0 B/op    0 allocs/op
// BenchmarkFibMemo-8       2000000   650 ns/op    800 B/op   15 allocs/op
// BenchmarkFibTab-8       10000000   120 ns/op    256 B/op    1 allocs/op
```

## JavaScript Testing with Jest
```
jest:
  what: JavaScript testing framework by Meta
  features:
    - Zero config for most projects
    - Snapshot testing
    - Built-in mocking
    - Code coverage
    - Parallel test execution
  commands:
    run_all: "npx jest"
    run_specific: "npx jest user.test.js"
    watch_mode: "npx jest --watch"
    coverage: "npx jest --coverage"
```

```javascript
// math.js
function add(a, b) {
  return a + b;
}

function divide(a, b) {
  if (b === 0) throw new Error("Division by zero");
  return a / b;
}

async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) throw new Error("User not found");
  return response.json();
}

module.exports = { add, divide, fetchUser };

// math.test.js
const { add, divide, fetchUser } = require("./math");

// Basic tests
describe("add", () => {
  test("adds positive numbers", () => {
    expect(add(2, 3)).toBe(5);
  });

  test("adds negative numbers", () => {
    expect(add(-1, -2)).toBe(-3);
  });

  test("adds zero", () => {
    expect(add(0, 0)).toBe(0);
  });
});

// Testing errors
describe("divide", () => {
  test("divides normally", () => {
    expect(divide(10, 2)).toBe(5);
  });

  test("throws on division by zero", () => {
    expect(() => divide(10, 0)).toThrow("Division by zero");
  });
});

// Mocking fetch
describe("fetchUser", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  test("returns user data", async () => {
    const mockUser = { id: 1, name: "Ankit" };
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    const user = await fetchUser(1);
    expect(user).toEqual(mockUser);
    expect(fetch).toHaveBeenCalledWith("/api/users/1");
  });

  test("throws on not found", async () => {
    global.fetch.mockResolvedValue({ ok: false });
    await expect(fetchUser(999)).rejects.toThrow("User not found");
  });
});

// Jest matchers cheat sheet
test("common matchers", () => {
  // Equality
  expect(1 + 1).toBe(2); // strict equality (===)
  expect({ a: 1 }).toEqual({ a: 1 }); // deep equality

  // Truthiness
  expect(null).toBeNull();
  expect(undefined).toBeUndefined();
  expect(true).toBeTruthy();
  expect(false).toBeFalsy();

  // Numbers
  expect(10).toBeGreaterThan(5);
  expect(0.1 + 0.2).toBeCloseTo(0.3);

  // Strings
  expect("hello world").toMatch(/world/);
  expect("hello").toContain("ell");

  // Arrays
  expect([1, 2, 3]).toContain(2);
  expect([1, 2, 3]).toHaveLength(3);

  // Objects
  expect({ name: "Ankit" }).toHaveProperty("name");
});
```

## When to Mock vs Real Dependencies
```
mock_vs_real:
  use_mocks_when:
    - External API calls (HTTP, gRPC)
    - Slow operations (file I/O, network)
    - Non-deterministic behavior (time, random)
    - Testing error paths (simulate failures)
    - Unit testing in isolation
    - Third-party services you don't control

  use_real_dependencies_when:
    - Database queries (use test DB or SQLite)
    - Integration tests
    - Testing SQL correctness
    - Testing actual serialization/deserialization
    - End-to-end flows

  use_fakes_when:
    - In-memory implementation of a repository
    - Simpler than mocks, more realistic than stubs
    - Example: in-memory map instead of real database

  test_doubles_terminology:
    dummy: Passed but never used (satisfy parameter list)
    stub: Returns predetermined values
    mock: Verifies interactions (was this method called?)
    fake: Working implementation with shortcuts (in-memory DB)
    spy: Records calls for later verification

  practical_advice:
    - If mocking is hard, your design probably needs improvement
    - Too many mocks = test is fragile and tests mocks, not code
    - Mock at the boundary (interfaces), not deep internals
    - If the mock setup is longer than the test, reconsider
```

## Testing Cheat Sheet
```
go_testing_cheat_sheet:
  commands:
    run_all: "go test ./..."
    run_verbose: "go test -v ./..."
    run_specific: "go test -run TestMyFunc ./..."
    run_with_race: "go test -race ./..."
    run_coverage: "go test -cover ./..."
    run_benchmarks: "go test -bench=. -benchmem ./..."
    run_integration: "go test -tags=integration ./..."
    short_mode: "go test -short ./..."  # skip slow tests

  naming_conventions:
    test_files: "*_test.go"
    test_functions: "TestXxx(t *testing.T)"
    benchmark_functions: "BenchmarkXxx(b *testing.B)"
    example_functions: "ExampleXxx()"
    test_helper: "t.Helper() at start of helper functions"

  testing_package_methods:
    t.Error: "Report failure, continue test"
    t.Errorf: "Report failure with format, continue test"
    t.Fatal: "Report failure, stop this test"
    t.Fatalf: "Report failure with format, stop this test"
    t.Skip: "Skip this test"
    t.Run: "Run subtest"
    t.Parallel: "Run this test in parallel"
    t.Cleanup: "Register cleanup function"
    t.TempDir: "Create temp directory, auto-cleaned"

jest_cheat_sheet:
  structure:
    describe: "Group related tests"
    test_or_it: "Individual test case"
    beforeAll: "Run once before all tests"
    afterAll: "Run once after all tests"
    beforeEach: "Run before each test"
    afterEach: "Run after each test"

  mocking:
    jest.fn: "Create a mock function"
    jest.mock: "Mock an entire module"
    jest.spyOn: "Spy on a method"
    mockReturnValue: "Set return value"
    mockResolvedValue: "Set async return value"
    mockRejectedValue: "Set async error"
```
