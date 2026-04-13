# Golang (Go)

Go is a **statically typed, compiled** language designed at Google for simplicity, concurrency, and performance. It compiles to a single binary with no dependencies.

---

## Setup & Basics

```bash
# Install (Linux/Mac)
# Download from https://go.dev/dl/

# Check version
go version

# Initialize a module (project)
go mod init github.com/yourname/projectname

# Run a file
go run main.go

# Build binary
go build -o myapp main.go

# Format code
go fmt ./...

# Run tests
go test ./...
```

### Hello World

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

- Every Go file belongs to a `package`
- `main` package + `main()` function = entry point
- Unused imports and variables are **compile errors** (not warnings)

---

## Variables & Types

### Declaration

```go
// Explicit type
var name string = "Ankit"
var age int = 25

// Type inference
var city = "Delhi"

// Short declaration (most common — only inside functions)
count := 10
pi := 3.14
active := true

// Multiple
x, y := 10, 20
var a, b, c int = 1, 2, 3

// Constants
const Pi = 3.14159
const (
    StatusOK    = 200
    StatusError = 500
)
```

### Basic Types

```go
// Numbers
int, int8, int16, int32, int64
uint, uint8, uint16, uint32, uint64
float32, float64
complex64, complex128

// Others
string
bool
byte    // alias for uint8
rune    // alias for int32 (Unicode code point)
```

### Zero Values (defaults when not initialized)

```go
var i int       // 0
var f float64   // 0.0
var b bool      // false
var s string    // ""
var p *int      // nil
var sl []int    // nil
var m map[string]int // nil
```

### Type Conversion (no implicit casting in Go)

```go
i := 42
f := float64(i)     // int → float64
s := string(65)      // int → string ("A" — Unicode)
s2 := strconv.Itoa(42)  // int → string "42"
n, _ := strconv.Atoi("42")  // string → int
```

---

## Strings

```go
import (
    "fmt"
    "strings"
)

s := "Hello, Go!"

// Length (bytes, not runes)
len(s)                    // 10

// Rune count (for Unicode)
utf8.RuneCountInString(s)

// Substring
s[0:5]                    // "Hello"

// Common operations
strings.Contains(s, "Go")          // true
strings.HasPrefix(s, "Hello")      // true
strings.HasSuffix(s, "!")          // true
strings.ToUpper(s)                 // "HELLO, GO!"
strings.ToLower(s)                 // "hello, go!"
strings.Replace(s, "Go", "World", 1)
strings.Split("a,b,c", ",")       // ["a", "b", "c"]
strings.Join([]string{"a","b"}, "-") // "a-b"
strings.TrimSpace("  hi  ")       // "hi"
strings.Index(s, "Go")            // 7

// String formatting
name := "Ankit"
fmt.Sprintf("Hello, %s! Age: %d", name, 25)  // "Hello, Ankit! Age: 25"

// Format verbs
// %s  string
// %d  integer
// %f  float          %.2f for 2 decimal places
// %v  default format (any type)
// %+v struct with field names
// %T  type of variable
// %p  pointer address
// %t  boolean
```

### Strings Builder (efficient concatenation)

```go
var b strings.Builder
for i := 0; i < 1000; i++ {
    b.WriteString("hello ")
}
result := b.String()
```

---

## Control Flow

### If / Else

```go
if x > 10 {
    fmt.Println("big")
} else if x > 5 {
    fmt.Println("medium")
} else {
    fmt.Println("small")
}

// If with initialization statement (scoped to if block)
if val, err := doSomething(); err != nil {
    fmt.Println("error:", err)
} else {
    fmt.Println("value:", val)
}
```

### Switch

```go
// No break needed — Go breaks automatically
switch day {
case "Monday":
    fmt.Println("Start of week")
case "Friday":
    fmt.Println("TGIF")
case "Saturday", "Sunday":
    fmt.Println("Weekend!")
default:
    fmt.Println("Midweek")
}

// Switch without condition (cleaner than if/else chains)
switch {
case score >= 90:
    grade = "A"
case score >= 80:
    grade = "B"
default:
    grade = "C"
}

// Type switch
switch v := i.(type) {
case int:
    fmt.Println("int:", v)
case string:
    fmt.Println("string:", v)
default:
    fmt.Println("unknown")
}
```

### For (the only loop in Go)

```go
// Classic for
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// While-style
for count < 100 {
    count++
}

// Infinite loop
for {
    // break to exit
    if done {
        break
    }
}

// Range over slice
nums := []int{10, 20, 30}
for index, value := range nums {
    fmt.Printf("index=%d value=%d\n", index, value)
}

// Range — ignore index
for _, value := range nums {
    fmt.Println(value)
}

// Range over map
for key, value := range myMap {
    fmt.Printf("%s: %v\n", key, value)
}

// Range over string (iterates runes, not bytes)
for i, ch := range "Hello" {
    fmt.Printf("%d: %c\n", i, ch)
}
```

---

## Functions

### Basic Functions

```go
func add(a int, b int) int {
    return a + b
}

// Same type shorthand
func add(a, b int) int {
    return a + b
}

// Multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 3)
if err != nil {
    log.Fatal(err)
}

// Named return values
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // naked return — returns x, y
}
```

### Variadic Functions

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3)        // 6
sum([]int{1,2,3}...)  // spread slice
```

### First-Class Functions & Closures

```go
// Function as variable
greet := func(name string) string {
    return "Hello, " + name
}
greet("Ankit")

// Function as parameter
func apply(nums []int, fn func(int) int) []int {
    result := make([]int, len(nums))
    for i, v := range nums {
        result[i] = fn(v)
    }
    return result
}

doubled := apply([]int{1, 2, 3}, func(n int) int {
    return n * 2
})
// [2, 4, 6]

// Closure — captures outer variable
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
c()  // 1
c()  // 2
c()  // 3
```

### Defer

`defer` schedules a function call to run **after** the surrounding function returns. Deferred calls execute in **LIFO** order.

```go
func readFile(path string) (string, error) {
    f, err := os.Open(path)
    if err != nil {
        return "", err
    }
    defer f.Close()  // guaranteed cleanup — runs when readFile returns

    data, err := io.ReadAll(f)
    if err != nil {
        return "", err
    }
    return string(data), nil
}

// LIFO order
defer fmt.Println("first")
defer fmt.Println("second")
defer fmt.Println("third")
// Output: third, second, first
```

### Init Function

```go
// init() runs automatically before main() — used for setup
// Each file can have its own init()
func init() {
    // initialize package-level variables, validate config, etc.
}
```

---

## Data Structures

### Arrays (fixed size — rarely used directly)

```go
var arr [5]int                  // [0, 0, 0, 0, 0]
arr2 := [3]string{"a", "b", "c"}
arr3 := [...]int{1, 2, 3, 4}   // compiler counts: [4]int
```

### Slices (dynamic — this is what you use)

```go
// Create
nums := []int{1, 2, 3, 4, 5}
empty := []int{}
made := make([]int, 5)       // length 5, zero-valued
withCap := make([]int, 0, 10) // length 0, capacity 10

// Access
nums[0]        // 1
nums[1:3]      // [2, 3]  — sub-slice
nums[:3]       // [1, 2, 3]
nums[2:]       // [3, 4, 5]

// Append
nums = append(nums, 6)
nums = append(nums, 7, 8, 9)
nums = append(nums, otherSlice...)

// Length and capacity
len(nums)
cap(nums)

// Copy
src := []int{1, 2, 3}
dst := make([]int, len(src))
copy(dst, src)

// Delete element at index i (order preserved)
nums = append(nums[:i], nums[i+1:]...)

// Check if slice is empty
if len(nums) == 0 {
    // empty
}

// slices package (Go 1.21+)
import "slices"
slices.Contains(nums, 3)          // true
slices.Sort(nums)                  // sort in-place
slices.Index(nums, 3)             // index of element
slices.Equal([]int{1,2}, []int{1,2}) // true
```

### Maps

```go
// Create
m := map[string]int{
    "alice": 25,
    "bob":   30,
}
m2 := make(map[string]int)  // empty map

// Access
age := m["alice"]       // 25
age2 := m["unknown"]    // 0 (zero value — not an error)

// Check existence
val, ok := m["alice"]
if ok {
    fmt.Println("found:", val)
}

// Set
m["charlie"] = 35

// Delete
delete(m, "bob")

// Length
len(m)

// Iterate (order is NOT guaranteed)
for key, value := range m {
    fmt.Printf("%s: %d\n", key, value)
}

// maps package (Go 1.21+)
import "maps"
maps.Keys(m)     // returns iterator of keys
maps.Values(m)   // returns iterator of values
```

---

## Structs

### Definition & Usage

```go
type User struct {
    ID        int
    Name      string
    Email     string
    Active    bool
    CreatedAt time.Time
}

// Create
u1 := User{
    ID:    1,
    Name:  "Ankit",
    Email: "ankit@example.com",
    Active: true,
}

u2 := User{Name: "Bob"}  // other fields get zero values

// Access
fmt.Println(u1.Name)
u1.Email = "new@example.com"

// Pointer to struct
u3 := &User{Name: "Charlie"}
u3.Name  // auto-dereferenced (no need for (*u3).Name)
```

### Methods

```go
// Value receiver — gets a copy (read-only)
func (u User) FullName() string {
    return u.Name
}

// Pointer receiver — can modify the struct
func (u *User) Deactivate() {
    u.Active = false
}

u := User{Name: "Ankit", Active: true}
u.FullName()     // "Ankit"
u.Deactivate()   // u.Active is now false
```

> **Rule of thumb:** Use pointer receivers when you need to mutate, or when the struct is large. Be consistent — if one method uses a pointer receiver, all methods on that type should.

### Struct Embedding (Composition over Inheritance)

```go
type Address struct {
    City    string
    Country string
}

type Employee struct {
    User              // embedded — Employee "inherits" User's fields and methods
    Address           // embedded
    Department string
}

e := Employee{
    User:       User{Name: "Ankit"},
    Address:    Address{City: "Delhi", Country: "India"},
    Department: "Engineering",
}

// Access promoted fields directly
e.Name      // "Ankit" (from User)
e.City      // "Delhi" (from Address)
e.FullName() // works — promoted from User
```

### Struct Tags

```go
type User struct {
    ID    int    `json:"id" db:"user_id"`
    Name  string `json:"name" validate:"required"`
    Email string `json:"email,omitempty"`   // omit if empty
    Pass  string `json:"-"`                  // always exclude from JSON
}

// Used by encoding/json, database drivers, validators, etc.
data, _ := json.Marshal(user)
// {"id":1,"name":"Ankit","email":"ankit@example.com"}
```

---

## Interfaces

Interfaces in Go are **implicit** — a type implements an interface by implementing its methods. No `implements` keyword.

```go
type Shape interface {
    Area() float64
    Perimeter() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

type Rectangle struct {
    Width, Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

// Both Circle and Rectangle implement Shape — no explicit declaration needed
func printShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}

printShapeInfo(Circle{Radius: 5})
printShapeInfo(Rectangle{Width: 3, Height: 4})
```

### Common Interfaces in stdlib

```go
// Stringer — like toString()
type Stringer interface {
    String() string
}

func (u User) String() string {
    return fmt.Sprintf("%s (%s)", u.Name, u.Email)
}

// Error
type error interface {
    Error() string
}

// io.Reader / io.Writer
type Reader interface {
    Read(p []byte) (n int, err error)
}
type Writer interface {
    Write(p []byte) (n int, err error)
}

// sort.Interface
type Interface interface {
    Len() int
    Less(i, j int) bool
    Swap(i, j int)
}
```

### Empty Interface & Type Assertions

```go
// any (alias for interface{}) — accepts any type
func printAnything(v any) {
    fmt.Println(v)
}

// Type assertion — extract concrete type
var i any = "hello"

s := i.(string)    // "hello" — panics if wrong type

s, ok := i.(string)  // safe — ok is false if wrong type
if ok {
    fmt.Println(s)
}
```

### Interface Composition

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

---

## Error Handling

Go uses **explicit error returns** instead of exceptions.

### Basic Pattern

```go
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doing something failed: %w", err)  // wrap with context
}
```

### Custom Errors

```go
// Simple
var ErrNotFound = errors.New("not found")
var ErrUnauthorized = errors.New("unauthorized")

// Custom error type
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error: %s - %s", e.Field, e.Message)
}

func validateAge(age int) error {
    if age < 0 {
        return &ValidationError{Field: "age", Message: "cannot be negative"}
    }
    return nil
}
```

### Error Wrapping & Unwrapping (Go 1.13+)

```go
// Wrap — adds context while preserving original error
if err != nil {
    return fmt.Errorf("failed to fetch user %d: %w", id, err)
}

// Check if error IS a specific error
if errors.Is(err, ErrNotFound) {
    // handle not found
}

// Extract specific error type
var validErr *ValidationError
if errors.As(err, &validErr) {
    fmt.Println("field:", validErr.Field)
}
```

### Panic & Recover (use sparingly — only for truly unrecoverable situations)

```go
// Panic — crashes the program
func mustParseConfig(path string) Config {
    cfg, err := parseConfig(path)
    if err != nil {
        panic("invalid config: " + err.Error())
    }
    return cfg
}

// Recover — catch a panic (only works inside defer)
func safeHandler() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("recovered from panic:", r)
        }
    }()
    riskyOperation()
}
```

---

## Generics (Go 1.18+)

```go
// Generic function
func Filter[T any](slice []T, predicate func(T) bool) []T {
    var result []T
    for _, v := range slice {
        if predicate(v) {
            result = append(result, v)
        }
    }
    return result
}

evens := Filter([]int{1, 2, 3, 4, 5}, func(n int) bool {
    return n%2 == 0
})
// [2, 4]

// Constrained generic
func Max[T cmp.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}

Max(3, 7)       // 7
Max("a", "z")   // "z"

// Generic struct
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

s := Stack[int]{}
s.Push(1)
s.Push(2)
val, ok := s.Pop()  // 2, true

// Custom constraint
type Number interface {
    int | int32 | int64 | float32 | float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}
```

---

## Concurrency

### Goroutines

Goroutines are lightweight threads managed by the Go runtime (~2KB stack, not OS threads).

```go
func fetchURL(url string) {
    resp, err := http.Get(url)
    if err != nil {
        fmt.Println("error:", err)
        return
    }
    defer resp.Body.Close()
    fmt.Println(url, resp.StatusCode)
}

// Launch goroutines
go fetchURL("https://example.com")
go fetchURL("https://google.com")

// Anonymous goroutine
go func() {
    fmt.Println("running in background")
}()
```

### Channels

Channels are the primary way goroutines communicate. They are **typed conduits** for sending and receiving values.

```go
// Unbuffered channel — sender blocks until receiver is ready
ch := make(chan string)

go func() {
    ch <- "hello"  // send
}()

msg := <-ch  // receive (blocks until value is sent)
fmt.Println(msg)

// Buffered channel — sender blocks only when buffer is full
ch := make(chan int, 3)
ch <- 1
ch <- 2
ch <- 3
// ch <- 4  // would block — buffer full

// Channel direction (in function signatures)
func producer(out chan<- int) {  // send-only
    out <- 42
}
func consumer(in <-chan int) {  // receive-only
    val := <-in
    fmt.Println(val)
}

// Close a channel — signals no more values
close(ch)

// Range over channel — reads until closed
go func() {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)
}()

for val := range ch {
    fmt.Println(val)
}
```

### Select

`select` waits on multiple channel operations — like `switch` for channels.

```go
func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- "one"
    }()
    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "two"
    }()

    // Wait for whichever arrives first
    select {
    case msg := <-ch1:
        fmt.Println("received from ch1:", msg)
    case msg := <-ch2:
        fmt.Println("received from ch2:", msg)
    case <-time.After(3 * time.Second):
        fmt.Println("timeout")
    }
}

// Non-blocking select
select {
case msg := <-ch:
    fmt.Println(msg)
default:
    fmt.Println("no message available")
}
```

### WaitGroup

Wait for multiple goroutines to finish.

```go
import "sync"

func main() {
    var wg sync.WaitGroup
    urls := []string{"url1", "url2", "url3"}

    for _, url := range urls {
        wg.Add(1)
        go func() {
            defer wg.Done()
            fetch(url)
        }()
    }

    wg.Wait()  // blocks until all goroutines call Done()
    fmt.Println("all done")
}
```

### Mutex

Protect shared state from concurrent access.

```go
type SafeCounter struct {
    mu    sync.Mutex
    count map[string]int
}

func (c *SafeCounter) Increment(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count[key]++
}

func (c *SafeCounter) Get(key string) int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count[key]
}

// RWMutex — multiple readers OR one writer
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func (c *Cache) Get(key string) string {
    c.mu.RLock()          // multiple goroutines can read simultaneously
    defer c.mu.RUnlock()
    return c.data[key]
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock()           // exclusive write access
    defer c.mu.Unlock()
    c.data[key] = value
}
```

### Context

Context carries deadlines, cancellation signals, and request-scoped values across API boundaries and goroutines.

```go
import "context"

// With timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// With cancellation
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// Use in HTTP request
req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.example.com", nil)
resp, err := http.DefaultClient.Do(req)

// Use in your own function
func fetchData(ctx context.Context, id int) (Data, error) {
    select {
    case <-ctx.Done():
        return Data{}, ctx.Err()  // context.Canceled or context.DeadlineExceeded
    case result := <-doWork(id):
        return result, nil
    }
}

// With value (use sparingly — prefer explicit params)
type contextKey string
const userIDKey contextKey = "userID"

ctx = context.WithValue(ctx, userIDKey, 42)
userID := ctx.Value(userIDKey).(int)
```

### Common Concurrency Patterns

#### Worker Pool

```go
func workerPool(jobs <-chan int, results chan<- int, numWorkers int) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for job := range jobs {
                fmt.Printf("worker %d processing job %d\n", workerID, job)
                results <- job * 2
            }
        }(i)
    }
    wg.Wait()
    close(results)
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    go workerPool(jobs, results, 5)

    // Send jobs
    for i := 0; i < 20; i++ {
        jobs <- i
    }
    close(jobs)

    // Collect results
    for r := range results {
        fmt.Println(r)
    }
}
```

#### Fan-out / Fan-in

```go
// Fan-out: multiple goroutines reading from the same channel
// Fan-in: merge multiple channels into one

func fanIn(channels ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    merged := make(chan int)

    for _, ch := range channels {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for val := range ch {
                merged <- val
            }
        }()
    }

    go func() {
        wg.Wait()
        close(merged)
    }()

    return merged
}
```

#### Semaphore (limit concurrency)

```go
func processWithLimit(items []string, maxConcurrent int) {
    sem := make(chan struct{}, maxConcurrent)
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        sem <- struct{}{}  // acquire slot (blocks if full)
        go func() {
            defer wg.Done()
            defer func() { <-sem }()  // release slot
            process(item)
        }()
    }

    wg.Wait()
}
```

---

## Pointers

```go
x := 42
p := &x      // p is *int — pointer to x
fmt.Println(*p)  // 42 — dereference
*p = 100     // x is now 100

// Pointer to struct
u := &User{Name: "Ankit"}
u.Name  // auto-dereferenced

// new() allocates zero-valued and returns pointer
p := new(int)   // *int pointing to 0

// nil pointer
var p *int  // nil
if p != nil {
    fmt.Println(*p)  // safe
}
```

**When to use pointers:**
- When you need to mutate the value
- For large structs (avoid copying)
- When `nil` is a meaningful value

---

## JSON

```go
import "encoding/json"

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
}

// Struct → JSON (Marshal)
user := User{ID: 1, Name: "Ankit", Email: "a@b.com"}
data, err := json.Marshal(user)
// {"id":1,"name":"Ankit","email":"a@b.com"}

// Pretty print
data, err := json.MarshalIndent(user, "", "  ")

// JSON → Struct (Unmarshal)
var u User
err := json.Unmarshal([]byte(`{"id":1,"name":"Ankit"}`), &u)

// Unknown structure — unmarshal to map
var result map[string]any
json.Unmarshal(data, &result)

// Streaming — Encoder/Decoder (for io.Reader/Writer, HTTP)
json.NewEncoder(w).Encode(user)   // write JSON to http.ResponseWriter
json.NewDecoder(r.Body).Decode(&user)  // read JSON from request body
```

---

## HTTP

### HTTP Server

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func main() {
    mux := http.NewServeMux()

    // GET /health
    mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("ok"))
    })

    // GET /users/{id}  (Go 1.22+ pattern matching)
    mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
        id := r.PathValue("id")
        user := User{ID: 1, Name: "Ankit"}
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(user)
    })

    // POST /users
    mux.HandleFunc("POST /users", func(w http.ResponseWriter, r *http.Request) {
        var user User
        if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
            http.Error(w, "bad request", http.StatusBadRequest)
            return
        }
        w.WriteHeader(http.StatusCreated)
        json.NewEncoder(w).Encode(user)
    })

    log.Println("server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
```

### Middleware

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}

// Chain middleware
handler := loggingMiddleware(authMiddleware(mux))
http.ListenAndServe(":8080", handler)
```

### HTTP Client

```go
// Simple GET
resp, err := http.Get("https://api.example.com/users")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

var users []User
json.NewDecoder(resp.Body).Decode(&users)

// Custom client with timeout
client := &http.Client{
    Timeout: 10 * time.Second,
}

// POST with JSON body
payload, _ := json.Marshal(User{Name: "Ankit"})
req, _ := http.NewRequest("POST", "https://api.example.com/users", bytes.NewBuffer(payload))
req.Header.Set("Content-Type", "application/json")
req.Header.Set("Authorization", "Bearer token123")

resp, err := client.Do(req)
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()
```

---

## File I/O

```go
import (
    "os"
    "bufio"
)

// Read entire file
data, err := os.ReadFile("config.json")

// Write entire file (creates or overwrites, permissions 0644)
err := os.WriteFile("output.txt", []byte("hello"), 0644)

// Line-by-line reading
file, err := os.Open("data.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}

// Append to file
f, err := os.OpenFile("log.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
if err != nil {
    log.Fatal(err)
}
defer f.Close()
f.WriteString("new log line\n")

// Check if file exists
if _, err := os.Stat("file.txt"); errors.Is(err, os.ErrNotExist) {
    fmt.Println("file does not exist")
}

// Create directory
os.Mkdir("newdir", 0755)
os.MkdirAll("path/to/nested/dir", 0755)  // mkdir -p
```

---

## Testing

```go
// math.go
package math

func Add(a, b int) int {
    return a + b
}

// math_test.go  (same package, file must end in _test.go)
package math

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}

// Table-driven tests (idiomatic Go)
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
        {"mixed", -1, 5, 4},
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

// Benchmarks
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(2, 3)
    }
}
// Run: go test -bench=.

// Test helpers
func TestSomething(t *testing.T) {
    t.Helper()  // marks this as a helper — errors report caller's line
    t.Skip("skipping this test")
    t.Parallel()  // run in parallel with other parallel tests
}
```

```bash
go test ./...              # all tests
go test -v ./...           # verbose
go test -run TestAdd       # specific test
go test -count=1 ./...     # no caching
go test -race ./...        # detect race conditions
go test -cover ./...       # coverage
go test -coverprofile=c.out && go tool cover -html=c.out  # HTML report
```

---

## Project Structure (Standard Layout)

```
myproject/
├── cmd/
│   └── server/
│       └── main.go          # entry point
├── internal/                 # private packages — can't be imported externally
│   ├── handler/
│   │   └── user.go
│   ├── service/
│   │   └── user.go
│   ├── repository/
│   │   └── user.go
│   └── model/
│       └── user.go
├── pkg/                      # public packages — can be imported by others
│   └── validator/
│       └── validator.go
├── api/                      # API specs (OpenAPI, proto files)
├── config/
├── go.mod
├── go.sum
└── Makefile
```

---

## Modules & Packages

```bash
# Initialize module
go mod init github.com/yourname/project

# Add dependency
go get github.com/gin-gonic/gin

# Remove unused dependencies
go mod tidy

# Vendor dependencies
go mod vendor
```

```go
// Importing
import (
    "fmt"                                      // stdlib
    "github.com/gin-gonic/gin"                // third-party
    "github.com/yourname/project/internal/handler"  // local
)

// Package visibility
// Uppercase = exported (public)    → User, GetName()
// Lowercase = unexported (private) → user, getName()
```

---

## Useful Stdlib Packages

| Package | Purpose |
|---|---|
| `fmt` | Formatted I/O, printing |
| `strings` | String manipulation |
| `strconv` | String ↔ number conversion |
| `os` | File system, env vars, process |
| `io` | Reader/Writer interfaces |
| `net/http` | HTTP client & server |
| `encoding/json` | JSON marshal/unmarshal |
| `log` / `log/slog` | Logging (slog is structured, Go 1.21+) |
| `time` | Time, duration, timers |
| `context` | Cancellation & deadlines |
| `sync` | Mutex, WaitGroup, Once, Pool |
| `errors` | Error wrapping, Is, As |
| `sort` / `slices` | Sorting |
| `regexp` | Regular expressions |
| `crypto/*` | Hashing, encryption |
| `database/sql` | Database interface |
| `testing` | Unit tests & benchmarks |
| `embed` | Embed files in binary |

---

## Slog — Structured Logging (Go 1.21+)

```go
import "log/slog"

// Default text logger
slog.Info("user created", "id", 42, "name", "Ankit")
// Output: 2024/01/15 10:30:00 INFO user created id=42 name=Ankit

// JSON logger
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelDebug,
}))
slog.SetDefault(logger)

slog.Debug("fetching data", "url", "https://api.example.com")
slog.Info("request completed", "status", 200, "duration", time.Since(start))
slog.Warn("rate limit approaching", "remaining", 10)
slog.Error("failed to connect", "err", err)

// With context
logger = logger.With("service", "user-api", "version", "1.0")
logger.Info("starting")  // every log includes service and version
```

---

## Embed (Go 1.16+)

Embed files directly into the compiled binary.

```go
import "embed"

//go:embed config.json
var configFile []byte

//go:embed templates/*.html
var templates embed.FS

//go:embed static
var staticFiles embed.FS  // entire directory

// Use with HTTP
http.Handle("/static/", http.FileServer(http.FS(staticFiles)))
```

---

## Quick Reference — Go Idioms

```go
// 1. Accept interfaces, return structs
func NewService(repo UserRepository) *UserService { ... }

// 2. Error first, happy path un-indented
if err != nil {
    return err
}
// continue with happy path...

// 3. Use short variable names in small scopes
for i, v := range items { ... }   // not index, value
for k, v := range m { ... }       // not key, value

// 4. Don't export unless you need to
type service struct { ... }  // unexported — internal

// 5. Use meaningful package names — no util, helper, common
package validator  // not package utils

// 6. Check errors — never use _ for errors in production code
result, err := doThing()  // not result, _ := doThing()

// 7. sync.Once for one-time initialization
var once sync.Once
var db *sql.DB

func getDB() *sql.DB {
    once.Do(func() {
        db, _ = sql.Open("postgres", connStr)
    })
    return db
}

// 8. Enums with iota
type Role int
const (
    Admin Role = iota  // 0
    Editor             // 1
    Viewer             // 2
)
```
