# Concurrency

## What is Concurrency
```
overview:
  definition: Managing multiple tasks that can make progress without waiting for each other
  concurrency_vs_parallelism:
    concurrency:
      what: Dealing with multiple things at once (structure)
      analogy: One chef juggling multiple dishes, switching between them
      example: Single-core CPU switching between goroutines
    parallelism:
      what: Doing multiple things at once (execution)
      analogy: Multiple chefs each cooking a different dish simultaneously
      example: Multi-core CPU running goroutines on different cores
    key_insight: >
      Concurrency is about structure, parallelism is about execution.
      You can have concurrency without parallelism (single core).
      Parallelism requires concurrency.

  why_it_matters:
    - Better resource utilization (don't block on I/O)
    - Improved responsiveness (serve multiple users)
    - Faster processing (utilize multiple CPU cores)
    - Real-world is inherently concurrent
```

## Threads vs Goroutines
```
comparison:
  os_threads:
    managed_by: Operating system
    stack_size: "~1-8 MB (fixed)"
    creation_cost: Expensive (system call to kernel)
    context_switch: Slow (kernel mode switch, ~1-10 microseconds)
    scheduling: OS scheduler (preemptive)
    max_practical: Thousands
    communication: Shared memory + locks

  goroutines:
    managed_by: Go runtime
    stack_size: "~2-8 KB (grows dynamically up to 1 GB)"
    creation_cost: Very cheap (just a function call)
    context_switch: Fast (user-space, ~200 nanoseconds)
    scheduling: Go scheduler (cooperative + preemptive since Go 1.14)
    max_practical: Millions
    communication: Channels (message passing) or shared memory + sync

  go_scheduler:
    model: "M:N scheduling (M goroutines on N OS threads)"
    components:
      G: Goroutine
      M: Machine (OS thread)
      P: Processor (logical CPU, GOMAXPROCS)
    how_it_works: >
      Each P has a local run queue of goroutines.
      M picks a P and runs goroutines from its queue.
      Work stealing: idle P steals from busy P's queue.
```

### Goroutine Basics
```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func main() {
    // Basic goroutine
    go func() {
        fmt.Println("Hello from goroutine")
    }()

    // Wait for goroutines with WaitGroup
    var wg sync.WaitGroup

    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Printf("Worker %d started\n", id)
            time.Sleep(time.Second)
            fmt.Printf("Worker %d done\n", id)
        }(i) // pass i by value to avoid closure bug
    }

    wg.Wait()
    fmt.Println("All workers done")
}
```

## Race Conditions
```
race_condition:
  what: Bug where behavior depends on timing/order of goroutine execution
  cause: Multiple goroutines access shared data and at least one writes
  result: Unpredictable behavior, data corruption, crashes

  detection:
    go_race_detector: "go run -race main.go"
    go_test_race: "go test -race ./..."
    note: Always run tests with -race in CI
```

### Race Condition Example
```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    // BAD: Race condition
    counter := 0
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter++ // DATA RACE: multiple goroutines read+write
        }()
    }
    wg.Wait()
    fmt.Println("Counter (wrong):", counter) // not always 1000

    // GOOD: Fix with mutex
    counter = 0
    var mu sync.Mutex

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            mu.Lock()
            counter++
            mu.Unlock()
        }()
    }
    wg.Wait()
    fmt.Println("Counter (correct):", counter) // always 1000

    // GOOD: Fix with atomic
    // import "sync/atomic"
    // var counter int64
    // atomic.AddInt64(&counter, 1)

    // GOOD: Fix with channel
    counterCh := make(chan int, 1000)
    for i := 0; i < 1000; i++ {
        go func() {
            counterCh <- 1
        }()
    }
    total := 0
    for i := 0; i < 1000; i++ {
        total += <-counterCh
    }
    fmt.Println("Counter (channel):", total) // always 1000
}
```

## Mutexes
```
mutex:
  what: Mutual exclusion lock - only one goroutine can hold it at a time
  types:
    sync.Mutex:
      what: Basic lock, only one goroutine can hold it
      methods: Lock(), Unlock()
    sync.RWMutex:
      what: Reader/writer lock - multiple readers OR one writer
      methods: RLock(), RUnlock(), Lock(), Unlock()
      use_when: Reads are much more frequent than writes

  best_practices:
    - Always use defer mu.Unlock() after Lock()
    - Keep critical sections as small as possible
    - Don't lock across function boundaries if avoidable
    - Prefer channels over mutexes when possible
    - Never copy a mutex (pass by pointer)
```

```go
package main

import (
    "fmt"
    "sync"
)

// Thread-safe cache with RWMutex
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func NewCache() *Cache {
    return &Cache{data: make(map[string]string)}
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock() // multiple readers allowed
    defer c.mu.RUnlock()
    val, ok := c.data[key]
    return val, ok
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock() // exclusive access
    defer c.mu.Unlock()
    c.data[key] = value
}

func (c *Cache) Delete(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    delete(c.data, key)
}

func main() {
    cache := NewCache()
    var wg sync.WaitGroup

    // Multiple writers
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            cache.Set(fmt.Sprintf("key-%d", id), fmt.Sprintf("value-%d", id))
        }(i)
    }

    wg.Wait()

    // Multiple readers
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            val, _ := cache.Get(fmt.Sprintf("key-%d", id))
            fmt.Println(val)
        }(i)
    }

    wg.Wait()
}
```

## Semaphores
```
semaphore:
  what: Controls access to a resource by limiting concurrent access to N goroutines
  vs_mutex: Mutex allows 1, semaphore allows N
  go_implementation: Buffered channel of capacity N
  use_cases:
    - Limit concurrent database connections
    - Rate limiting API calls
    - Control parallel file processing
```

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// Semaphore using buffered channel
type Semaphore struct {
    ch chan struct{}
}

func NewSemaphore(maxConcurrency int) *Semaphore {
    return &Semaphore{ch: make(chan struct{}, maxConcurrency)}
}

func (s *Semaphore) Acquire() {
    s.ch <- struct{}{} // blocks if channel is full
}

func (s *Semaphore) Release() {
    <-s.ch
}

func main() {
    sem := NewSemaphore(3) // max 3 concurrent
    var wg sync.WaitGroup

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            sem.Acquire()
            defer sem.Release()

            fmt.Printf("Worker %d running\n", id)
            time.Sleep(time.Second) // simulate work
            fmt.Printf("Worker %d done\n", id)
        }(i)
    }

    wg.Wait()
}
```

## Deadlocks
```
deadlock:
  what: Two or more goroutines waiting for each other to release resources, none can proceed
  conditions_all_four_needed:
    mutual_exclusion: Resource held exclusively by one goroutine
    hold_and_wait: Goroutine holds one resource while waiting for another
    no_preemption: Resources can't be forcibly taken away
    circular_wait: A waits for B, B waits for A

  prevention:
    - Always acquire locks in the same order
    - Use timeouts (context.WithTimeout)
    - Use channels instead of mutexes
    - Keep lock scope minimal
    - Avoid nested locks when possible

  go_detection: Go runtime detects simple deadlocks and panics with "fatal error: all goroutines are asleep"
```

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

// DEADLOCK example (DO NOT DO THIS)
func deadlockExample() {
    var mu1, mu2 sync.Mutex

    // Goroutine 1: locks mu1, then tries mu2
    go func() {
        mu1.Lock()
        time.Sleep(time.Millisecond)
        mu2.Lock() // blocks - mu2 is held by goroutine 2
        mu2.Unlock()
        mu1.Unlock()
    }()

    // Goroutine 2: locks mu2, then tries mu1
    go func() {
        mu2.Lock()
        time.Sleep(time.Millisecond)
        mu1.Lock() // blocks - mu1 is held by goroutine 1
        mu1.Unlock()
        mu2.Unlock()
    }()
    // DEADLOCK: both goroutines waiting for each other
}

// FIX: Always lock in the same order
func noDeadlock() {
    var mu1, mu2 sync.Mutex

    acquire := func() {
        mu1.Lock() // always lock mu1 first
        mu2.Lock() // then mu2
        defer mu2.Unlock()
        defer mu1.Unlock()
        // do work
    }

    go acquire()
    go acquire()
}

// FIX: Use context timeout to avoid hanging forever
func withTimeout() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()

    ch := make(chan string)
    go func() {
        time.Sleep(5 * time.Second) // simulate slow work
        ch <- "result"
    }()

    select {
    case result := <-ch:
        fmt.Println("Got:", result)
    case <-ctx.Done():
        fmt.Println("Timeout! Avoiding potential deadlock.")
    }
}
```

## Channels
```
channels:
  what: Typed conduits for communication between goroutines
  philosophy: "Don't communicate by sharing memory, share memory by communicating"
  types:
    unbuffered: "make(chan int) - sender blocks until receiver is ready"
    buffered: "make(chan int, 10) - sender blocks only when buffer is full"

  operations:
    send: "ch <- value"
    receive: "value := <-ch"
    close: "close(ch) - signals no more values, receivers get zero value"
    range: "for v := range ch - reads until channel is closed"
    select: "select on multiple channels, like a switch for channels"

  direction:
    send_only: "chan<- int"
    receive_only: "<-chan int"
    bidirectional: "chan int"
```

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    // Unbuffered channel - synchronous handoff
    ch := make(chan string)
    go func() {
        ch <- "hello" // blocks until someone receives
    }()
    msg := <-ch // blocks until someone sends
    fmt.Println(msg)

    // Buffered channel - async up to buffer size
    buffered := make(chan int, 3)
    buffered <- 1 // doesn't block
    buffered <- 2 // doesn't block
    buffered <- 3 // doesn't block
    // buffered <- 4 // would block - buffer full

    // Select - multiplexing channels
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(100 * time.Millisecond)
        ch1 <- "from ch1"
    }()
    go func() {
        time.Sleep(200 * time.Millisecond)
        ch2 <- "from ch2"
    }()

    // Receive from whichever is ready first
    select {
    case msg := <-ch1:
        fmt.Println(msg)
    case msg := <-ch2:
        fmt.Println(msg)
    case <-time.After(time.Second):
        fmt.Println("timeout")
    }

    // Range over channel
    numbers := make(chan int)
    go func() {
        for i := 0; i < 5; i++ {
            numbers <- i
        }
        close(numbers) // must close for range to stop
    }()
    for n := range numbers {
        fmt.Println(n) // 0, 1, 2, 3, 4
    }

    // Check if channel is closed
    ch3 := make(chan int)
    close(ch3)
    val, ok := <-ch3
    fmt.Println(val, ok) // 0, false (zero value, not ok)
}
```

## Worker Pools
```
worker_pool:
  what: Fixed number of goroutines processing jobs from a shared queue
  why:
    - Control resource usage (don't spawn unlimited goroutines)
    - Limit concurrent database connections, API calls
    - Reuse goroutines for multiple jobs
  pattern:
    1: Create a jobs channel
    2: Create a results channel
    3: Start N worker goroutines
    4: Send jobs into the jobs channel
    5: Collect results from the results channel
```

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// Simple worker pool
func workerPool() {
    const numWorkers = 3
    const numJobs = 10

    jobs := make(chan int, numJobs)
    results := make(chan int, numJobs)

    // Start workers
    var wg sync.WaitGroup
    for w := 0; w < numWorkers; w++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for job := range jobs {
                fmt.Printf("Worker %d processing job %d\n", id, job)
                time.Sleep(100 * time.Millisecond)
                results <- job * 2
            }
        }(w)
    }

    // Send jobs
    for j := 0; j < numJobs; j++ {
        jobs <- j
    }
    close(jobs)

    // Wait for workers, then close results
    go func() {
        wg.Wait()
        close(results)
    }()

    // Collect results
    for result := range results {
        fmt.Println("Result:", result)
    }
}

// Generic worker pool with error handling
type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID int
    Output string
    Err    error
}

func processJob(job Job) Result {
    // simulate processing
    time.Sleep(50 * time.Millisecond)
    return Result{
        JobID:  job.ID,
        Output: fmt.Sprintf("processed: %s", job.Data),
    }
}

func genericWorkerPool(jobs []Job, numWorkers int) []Result {
    jobCh := make(chan Job, len(jobs))
    resultCh := make(chan Result, len(jobs))

    // Start workers
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobCh {
                resultCh <- processJob(job)
            }
        }()
    }

    // Send jobs
    for _, job := range jobs {
        jobCh <- job
    }
    close(jobCh)

    // Close results when all workers done
    go func() {
        wg.Wait()
        close(resultCh)
    }()

    // Collect
    var results []Result
    for r := range resultCh {
        results = append(results, r)
    }
    return results
}

func main() {
    workerPool()
}
```

## Go Concurrency Patterns

### Fan-Out, Fan-In
```
fan_out_fan_in:
  fan_out: Distribute work from one channel to multiple goroutines
  fan_in: Merge results from multiple channels into one channel
  use_case: Parallel processing of independent tasks
```

```go
package main

import (
    "fmt"
    "sync"
)

// Fan-out: one input, multiple workers
// Fan-in: multiple outputs merged into one
func fanOutFanIn() {
    input := generateNumbers(1, 20)

    // Fan-out: start multiple workers on the same input channel
    numWorkers := 4
    workers := make([]<-chan int, numWorkers)
    for i := 0; i < numWorkers; i++ {
        workers[i] = squareNumbers(input)
    }

    // Fan-in: merge all worker outputs into one channel
    for result := range merge(workers...) {
        fmt.Println(result)
    }
}

func generateNumbers(start, end int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for i := start; i <= end; i++ {
            out <- i
        }
    }()
    return out
}

func squareNumbers(input <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range input {
            out <- n * n
        }
    }()
    return out
}

func merge(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}

func main() {
    fanOutFanIn()
}
```

### Pipeline
```
pipeline:
  what: Chain of stages where each stage is a goroutine, connected by channels
  each_stage:
    - Receives values from upstream via inbound channel
    - Performs some function on that data
    - Sends values downstream via outbound channel
  use_case: Data transformation pipelines, ETL, stream processing
```

```go
package main

import "fmt"

// Pipeline: generate -> double -> filter -> print
func main() {
    // Stage 1: Generate numbers
    nums := gen(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    // Stage 2: Double each number
    doubled := transform(nums, func(n int) int { return n * 2 })

    // Stage 3: Filter (keep only > 10)
    filtered := filter(doubled, func(n int) bool { return n > 10 })

    // Stage 4: Consume
    for v := range filtered {
        fmt.Println(v) // 12, 14, 16, 18, 20
    }
}

func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

func transform(in <-chan int, fn func(int) int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- fn(n)
        }
    }()
    return out
}

func filter(in <-chan int, predicate func(int) bool) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            if predicate(n) {
                out <- n
            }
        }
    }()
    return out
}
```

### Context Cancellation
```
context:
  what: Carry deadlines, cancellation signals, and request-scoped values across API boundaries
  types:
    context.Background: Top-level, never cancelled, root of all contexts
    context.TODO: Placeholder when unsure which context to use
    context.WithCancel: Manually cancellable
    context.WithTimeout: Auto-cancels after duration
    context.WithDeadline: Auto-cancels at specific time
    context.WithValue: Carry request-scoped data (use sparingly)

  rules:
    - Always pass context as first parameter
    - Never store context in a struct
    - Never pass nil context, use context.TODO() if unsure
    - context.WithValue is for request-scoped data only (trace ID, auth token)
```

```go
package main

import (
    "context"
    "fmt"
    "time"
)

// Cancel long-running work
func longRunningTask(ctx context.Context) error {
    for i := 0; i < 100; i++ {
        select {
        case <-ctx.Done():
            fmt.Println("Task cancelled:", ctx.Err())
            return ctx.Err()
        default:
            fmt.Printf("Working... step %d\n", i)
            time.Sleep(100 * time.Millisecond)
        }
    }
    return nil
}

// HTTP-style handler with timeout
func fetchData(ctx context.Context, url string) (string, error) {
    resultCh := make(chan string, 1)
    errCh := make(chan error, 1)

    go func() {
        // Simulate slow HTTP call
        time.Sleep(2 * time.Second)
        resultCh <- "data from " + url
    }()

    select {
    case result := <-resultCh:
        return result, nil
    case err := <-errCh:
        return "", err
    case <-ctx.Done():
        return "", ctx.Err()
    }
}

func main() {
    // WithCancel - manual cancellation
    ctx, cancel := context.WithCancel(context.Background())
    go func() {
        time.Sleep(500 * time.Millisecond)
        cancel() // cancel after 500ms
    }()
    longRunningTask(ctx)

    // WithTimeout - automatic cancellation
    ctx2, cancel2 := context.WithTimeout(context.Background(), 1*time.Second)
    defer cancel2() // always defer cancel to release resources

    result, err := fetchData(ctx2, "https://api.example.com")
    if err != nil {
        fmt.Println("Error:", err) // context deadline exceeded
    } else {
        fmt.Println("Result:", result)
    }

    // WithValue - pass request-scoped data
    type contextKey string
    const requestIDKey contextKey = "requestID"

    ctx3 := context.WithValue(context.Background(), requestIDKey, "req-123")
    processRequest(ctx3)
}

func processRequest(ctx context.Context) {
    type contextKey string
    const requestIDKey contextKey = "requestID"
    reqID := ctx.Value(requestIDKey).(string)
    fmt.Println("Processing request:", reqID)
}
```

## Node.js Event Loop
```
nodejs_event_loop:
  what: Single-threaded event-driven architecture that handles async I/O
  key_concept: >
    Node.js is single-threaded for JavaScript execution but uses
    a thread pool (libuv) for I/O operations. The event loop
    coordinates between the two.

  phases:
    1_timers: "Execute setTimeout and setInterval callbacks"
    2_pending_callbacks: "Execute I/O callbacks deferred from previous iteration"
    3_idle_prepare: "Internal use only"
    4_poll: "Retrieve new I/O events, execute I/O callbacks (most callbacks run here)"
    5_check: "Execute setImmediate callbacks"
    6_close_callbacks: "Execute close event callbacks (socket.on('close'))"

  microtask_queue:
    what: Runs BETWEEN each phase of the event loop
    includes:
      - Promise callbacks (.then, .catch, .finally)
      - process.nextTick callbacks (runs before promises)
    priority: process.nextTick > Promises > macrotasks

  key_insight: >
    JavaScript code never runs in parallel in Node.js.
    Only one piece of JS runs at a time.
    Async I/O happens in background threads (libuv),
    callbacks are queued and run when JS is free.

  blocking_the_loop:
    problem: CPU-intensive code blocks all other operations
    solutions:
      - Worker threads (worker_threads module)
      - Child processes (child_process module)
      - Offload to external service
      - Break work into chunks with setImmediate
```

```javascript
// Event loop demonstration

// 1. Synchronous code runs first
console.log("1. Sync start");

// 2. setTimeout - goes to timers phase
setTimeout(() => console.log("5. setTimeout"), 0);

// 3. setImmediate - goes to check phase
setImmediate(() => console.log("6. setImmediate"));

// 4. Promise - goes to microtask queue (runs before timers)
Promise.resolve().then(() => console.log("3. Promise.then"));

// 5. process.nextTick - highest priority microtask
process.nextTick(() => console.log("2. process.nextTick"));

// 6. Sync code runs first
console.log("1. Sync end");

// Output order:
// 1. Sync start
// 1. Sync end
// 2. process.nextTick
// 3. Promise.then
// 5. setTimeout
// 6. setImmediate

// Non-blocking I/O example
const fs = require("fs");

// This does NOT block the event loop
fs.readFile("big-file.txt", (err, data) => {
  // Callback runs when I/O is complete
  // The thread pool (libuv) handled the actual file read
  console.log("File read complete");
});

console.log("This runs immediately, doesn't wait for file");

// Blocking the event loop (BAD)
function badCpuWork() {
  const start = Date.now();
  while (Date.now() - start < 5000) {} // blocks for 5 seconds
  // Nothing else can run during this time
}

// Non-blocking CPU work (GOOD)
function goodCpuWork(data, callback) {
  const chunk = data.splice(0, 100);
  processChunk(chunk);
  if (data.length > 0) {
    setImmediate(() => goodCpuWork(data, callback));
  } else {
    callback();
  }
}

// Worker threads for CPU-intensive work (GOOD)
const { Worker, isMainThread, parentPort } = require("worker_threads");

if (isMainThread) {
  const worker = new Worker(__filename);
  worker.on("message", (result) => {
    console.log("Result from worker:", result);
  });
  worker.postMessage({ task: "heavy-computation" });
} else {
  parentPort.on("message", (msg) => {
    // Runs on separate thread, doesn't block main event loop
    const result = heavyComputation(msg.task);
    parentPort.postMessage(result);
  });
}
```

## Concurrency Cheat Sheet
```
go_concurrency_cheat_sheet:
  tool:                   when_to_use
  goroutine:              Any concurrent task
  channel:                Communication between goroutines
  sync.WaitGroup:         Wait for group of goroutines to finish
  sync.Mutex:             Protect shared data (simple)
  sync.RWMutex:           Protect shared data (read-heavy)
  sync.Once:              One-time initialization
  sync.Map:               Concurrent map (when keys are stable)
  context:                Cancellation, timeouts, request-scoped data
  select:                 Multiplex channels, timeouts
  buffered_channel:       Semaphore, rate limiting

  patterns:
    worker_pool:       Fixed goroutines processing jobs from channel
    fan_out_fan_in:    Distribute work, merge results
    pipeline:          Chain of processing stages
    pub_sub:           Broadcast events to multiple subscribers
    rate_limiter:      Control throughput with ticker or token bucket
    circuit_breaker:   Stop calling failing service, recover gracefully

  common_mistakes:
    - Goroutine leak (goroutine blocked forever, no way to stop it)
    - Closure capturing loop variable (use parameter instead)
    - Sending to closed channel (panics)
    - Not closing channels (range blocks forever)
    - Forgetting context cancellation (resource leak)
```
