# Data Structures

## What are Data Structures
```
overview:
  definition: Ways to organize, store, and manage data efficiently
  why_they_matter:
    - Choosing the right structure determines performance
    - Directly impacts time and space complexity
    - Foundation of every algorithm and system design
  categories:
    linear: Arrays, Linked Lists, Stacks, Queues
    hashing: Hash Maps, Hash Sets
    trees: BST, AVL, Heaps, Tries
    graphs: Directed, Undirected, Weighted
```

## Arrays
```
array:
  what: Contiguous block of memory storing elements of the same type
  indexing: Zero-based (arr[0] is first element)

  time_complexity:
    access_by_index: O(1)
    search_unsorted: O(n)
    search_sorted: O(log n)  # binary search
    insert_at_end: O(1)      # amortized for dynamic arrays
    insert_at_index: O(n)    # shift elements right
    delete_at_index: O(n)    # shift elements left

  space_complexity: O(n)

  when_to_use:
    - Need fast index-based access
    - Know the size in advance or size rarely changes
    - Iterating through all elements frequently
    - Cache-friendly traversal matters (contiguous memory)

  when_to_avoid:
    - Frequent insertions/deletions in the middle
    - Size is highly dynamic and unpredictable
```

### Go Implementation
```go
package main

import "fmt"

func main() {
    // Fixed-size array
    var arr [5]int
    arr[0] = 10
    arr[1] = 20

    // Slice (dynamic array) - more common in Go
    slice := []int{1, 2, 3, 4, 5}

    // Append (amortized O(1))
    slice = append(slice, 6)

    // Insert at index 2 - O(n)
    index := 2
    slice = append(slice[:index+1], slice[index:]...)
    slice[index] = 99

    // Delete at index 2 - O(n)
    slice = append(slice[:index], slice[index+1:]...)

    // Iterate
    for i, v := range slice {
        fmt.Printf("index=%d value=%d\n", i, v)
    }

    // Two-dimensional slice
    matrix := make([][]int, 3)
    for i := range matrix {
        matrix[i] = make([]int, 3)
    }
}
```

## Linked Lists
```
linked_list:
  what: Sequence of nodes where each node points to the next
  types:
    singly: Each node has data + pointer to next
    doubly: Each node has data + pointer to next + pointer to prev
    circular: Last node points back to first

  time_complexity:
    access_by_index: O(n)
    search: O(n)
    insert_at_head: O(1)
    insert_at_tail: O(1)  # if tail pointer maintained
    insert_at_middle: O(n)  # O(1) if you have the node reference
    delete_at_head: O(1)
    delete_at_middle: O(n)  # O(1) if you have the node reference

  space_complexity: O(n)

  when_to_use:
    - Frequent insertions/deletions at the beginning
    - Don't need random access by index
    - Implementing stacks, queues, LRU caches
    - Size changes frequently

  when_to_avoid:
    - Need fast random access
    - Memory is constrained (extra pointer overhead)
    - Cache performance matters (nodes scattered in memory)
```

### Go Implementation
```go
package main

import "fmt"

// Singly Linked List
type Node struct {
    Val  int
    Next *Node
}

type LinkedList struct {
    Head *Node
    Tail *Node
    Size int
}

func NewLinkedList() *LinkedList {
    return &LinkedList{}
}

// InsertAtHead - O(1)
func (ll *LinkedList) InsertAtHead(val int) {
    node := &Node{Val: val, Next: ll.Head}
    ll.Head = node
    if ll.Tail == nil {
        ll.Tail = node
    }
    ll.Size++
}

// InsertAtTail - O(1)
func (ll *LinkedList) InsertAtTail(val int) {
    node := &Node{Val: val}
    if ll.Tail != nil {
        ll.Tail.Next = node
    } else {
        ll.Head = node
    }
    ll.Tail = node
    ll.Size++
}

// DeleteAtHead - O(1)
func (ll *LinkedList) DeleteAtHead() (int, bool) {
    if ll.Head == nil {
        return 0, false
    }
    val := ll.Head.Val
    ll.Head = ll.Head.Next
    if ll.Head == nil {
        ll.Tail = nil
    }
    ll.Size--
    return val, true
}

// Search - O(n)
func (ll *LinkedList) Search(val int) *Node {
    curr := ll.Head
    for curr != nil {
        if curr.Val == val {
            return curr
        }
        curr = curr.Next
    }
    return nil
}

// Reverse - O(n)
func (ll *LinkedList) Reverse() {
    var prev *Node
    curr := ll.Head
    ll.Tail = ll.Head
    for curr != nil {
        next := curr.Next
        curr.Next = prev
        prev = curr
        curr = next
    }
    ll.Head = prev
}

func (ll *LinkedList) Print() {
    curr := ll.Head
    for curr != nil {
        fmt.Printf("%d -> ", curr.Val)
        curr = curr.Next
    }
    fmt.Println("nil")
}
```

## Stacks
```
stack:
  what: LIFO (Last In, First Out) data structure
  operations:
    push: Add element to top
    pop: Remove element from top
    peek: View top element without removing

  time_complexity:
    push: O(1)
    pop: O(1)
    peek: O(1)
    search: O(n)

  space_complexity: O(n)

  when_to_use:
    - Undo/redo functionality
    - Expression parsing (balanced parentheses)
    - DFS traversal (iterative)
    - Function call stack simulation
    - Backtracking algorithms
    - Browser history (back button)
```

### Go Implementation
```go
package main

import "fmt"

type Stack struct {
    items []int
}

func (s *Stack) Push(val int) {
    s.items = append(s.items, val)
}

func (s *Stack) Pop() (int, bool) {
    if len(s.items) == 0 {
        return 0, false
    }
    val := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return val, true
}

func (s *Stack) Peek() (int, bool) {
    if len(s.items) == 0 {
        return 0, false
    }
    return s.items[len(s.items)-1], true
}

func (s *Stack) IsEmpty() bool {
    return len(s.items) == 0
}

// Classic interview problem: valid parentheses
func isValidParentheses(s string) bool {
    stack := &Stack{}
    pairs := map[rune]rune{')': '(', ']': '[', '}': '{'}

    for _, ch := range s {
        if ch == '(' || ch == '[' || ch == '{' {
            stack.Push(int(ch))
        } else {
            top, ok := stack.Pop()
            if !ok || rune(top) != pairs[ch] {
                return false
            }
        }
    }
    return stack.IsEmpty()
}

func main() {
    fmt.Println(isValidParentheses("({[]})")) // true
    fmt.Println(isValidParentheses("({[})"))  // false
}
```

## Queues
```
queue:
  what: FIFO (First In, First Out) data structure
  operations:
    enqueue: Add element to back
    dequeue: Remove element from front
    peek: View front element without removing

  time_complexity:
    enqueue: O(1)
    dequeue: O(1)
    peek: O(1)
    search: O(n)

  space_complexity: O(n)

  variants:
    simple_queue: Basic FIFO
    circular_queue: Wraps around, fixed size, reuses space
    priority_queue: Elements dequeued by priority, not insertion order
    deque: Double-ended, insert/remove from both ends

  when_to_use:
    - BFS traversal
    - Task scheduling / job queues
    - Rate limiting / throttling
    - Message queues (Kafka, RabbitMQ)
    - Print spooling, CPU scheduling
```

### Go Implementation
```go
package main

import "fmt"

// Queue using slice
type Queue struct {
    items []int
}

func (q *Queue) Enqueue(val int) {
    q.items = append(q.items, val)
}

func (q *Queue) Dequeue() (int, bool) {
    if len(q.items) == 0 {
        return 0, false
    }
    val := q.items[0]
    q.items = q.items[1:]
    return val, true
}

func (q *Queue) Peek() (int, bool) {
    if len(q.items) == 0 {
        return 0, false
    }
    return q.items[0], true
}

func (q *Queue) IsEmpty() bool {
    return len(q.items) == 0
}

// Circular queue with fixed capacity
type CircularQueue struct {
    items    []int
    head     int
    tail     int
    size     int
    capacity int
}

func NewCircularQueue(capacity int) *CircularQueue {
    return &CircularQueue{
        items:    make([]int, capacity),
        capacity: capacity,
    }
}

func (cq *CircularQueue) Enqueue(val int) bool {
    if cq.size == cq.capacity {
        return false // full
    }
    cq.items[cq.tail] = val
    cq.tail = (cq.tail + 1) % cq.capacity
    cq.size++
    return true
}

func (cq *CircularQueue) Dequeue() (int, bool) {
    if cq.size == 0 {
        return 0, false
    }
    val := cq.items[cq.head]
    cq.head = (cq.head + 1) % cq.capacity
    cq.size--
    return val, true
}

func main() {
    q := &Queue{}
    q.Enqueue(1)
    q.Enqueue(2)
    q.Enqueue(3)
    for !q.IsEmpty() {
        val, _ := q.Dequeue()
        fmt.Println(val) // 1, 2, 3
    }
}
```

## Hash Maps
```
hash_map:
  what: Key-value store using a hash function to compute index into array of buckets
  how_it_works:
    1: Hash function converts key to integer
    2: Index = hash % array_size
    3: Store key-value pair at that index
    4: Handle collisions via chaining (linked list) or open addressing

  time_complexity:
    insert: O(1) average, O(n) worst case
    delete: O(1) average, O(n) worst case
    search: O(1) average, O(n) worst case
    note: Worst case when all keys hash to same bucket

  space_complexity: O(n)

  collision_handling:
    chaining: Each bucket holds a linked list of entries
    open_addressing: Find next empty slot (linear probing, quadratic probing)

  when_to_use:
    - Fast lookups by key
    - Counting frequencies
    - Caching / memoization
    - Deduplication
    - Two-sum type problems
    - Implementing sets

  when_to_avoid:
    - Need ordered data (use tree map instead)
    - Keys are not hashable
```

### Go Implementation
```go
package main

import "fmt"

// Go's built-in map is a hash map
func main() {
    // Create map
    m := make(map[string]int)
    m["alice"] = 25
    m["bob"] = 30

    // Lookup with existence check
    if age, ok := m["alice"]; ok {
        fmt.Println("Alice's age:", age)
    }

    // Delete
    delete(m, "bob")

    // Iterate (order is random)
    for key, val := range m {
        fmt.Printf("%s: %d\n", key, val)
    }

    // Frequency counter - classic pattern
    words := []string{"go", "rust", "go", "python", "go", "rust"}
    freq := make(map[string]int)
    for _, w := range words {
        freq[w]++
    }
    fmt.Println(freq) // map[go:3 python:1 rust:2]

    // Two Sum using hash map - O(n)
    nums := []int{2, 7, 11, 15}
    target := 9
    seen := make(map[int]int) // value -> index
    for i, num := range nums {
        complement := target - num
        if j, ok := seen[complement]; ok {
            fmt.Printf("Two Sum: [%d, %d]\n", j, i)
            break
        }
        seen[num] = i
    }
}

// Simple hash map implementation from scratch
type Entry struct {
    Key   string
    Value int
    Next  *Entry
}

type HashMap struct {
    buckets []*Entry
    size    int
}

func NewHashMap(capacity int) *HashMap {
    return &HashMap{
        buckets: make([]*Entry, capacity),
    }
}

func (hm *HashMap) hash(key string) int {
    h := 0
    for _, ch := range key {
        h = h*31 + int(ch)
    }
    if h < 0 {
        h = -h
    }
    return h % len(hm.buckets)
}

func (hm *HashMap) Put(key string, value int) {
    idx := hm.hash(key)
    curr := hm.buckets[idx]
    for curr != nil {
        if curr.Key == key {
            curr.Value = value // update
            return
        }
        curr = curr.Next
    }
    // Insert at head of chain
    entry := &Entry{Key: key, Value: value, Next: hm.buckets[idx]}
    hm.buckets[idx] = entry
    hm.size++
}

func (hm *HashMap) Get(key string) (int, bool) {
    idx := hm.hash(key)
    curr := hm.buckets[idx]
    for curr != nil {
        if curr.Key == key {
            return curr.Value, true
        }
        curr = curr.Next
    }
    return 0, false
}
```

## Trees

### Binary Search Tree (BST)
```
binary_search_tree:
  what: Tree where left child < parent < right child
  properties:
    - Each node has at most 2 children
    - In-order traversal gives sorted output
    - No duplicate values (typically)

  time_complexity:
    search: O(log n) average, O(n) worst (skewed)
    insert: O(log n) average, O(n) worst
    delete: O(log n) average, O(n) worst
    in_order_traversal: O(n)

  space_complexity: O(n)

  when_to_use:
    - Need sorted data with fast insert/delete
    - Range queries
    - In-order predecessor/successor
    - Hierarchical data
```

### AVL Tree
```
avl_tree:
  what: Self-balancing BST where height difference of left and right subtrees is at most 1
  balance_factor: height(left) - height(right), must be -1, 0, or 1

  rotations:
    left_rotation: When right-heavy (balance factor < -1)
    right_rotation: When left-heavy (balance factor > 1)
    left_right: Left rotate left child, then right rotate node
    right_left: Right rotate right child, then left rotate node

  time_complexity:
    search: O(log n) guaranteed
    insert: O(log n) guaranteed
    delete: O(log n) guaranteed
    note: No worst case O(n) like plain BST

  when_to_use:
    - Need guaranteed O(log n) operations
    - Frequent lookups (AVL is more strictly balanced than Red-Black)
    - Database indexing
```

### BST Go Implementation
```go
package main

import "fmt"

type TreeNode struct {
    Val   int
    Left  *TreeNode
    Right *TreeNode
}

type BST struct {
    Root *TreeNode
}

// Insert - O(log n) average
func (t *BST) Insert(val int) {
    t.Root = insertNode(t.Root, val)
}

func insertNode(node *TreeNode, val int) *TreeNode {
    if node == nil {
        return &TreeNode{Val: val}
    }
    if val < node.Val {
        node.Left = insertNode(node.Left, val)
    } else if val > node.Val {
        node.Right = insertNode(node.Right, val)
    }
    return node
}

// Search - O(log n) average
func (t *BST) Search(val int) bool {
    return searchNode(t.Root, val)
}

func searchNode(node *TreeNode, val int) bool {
    if node == nil {
        return false
    }
    if val == node.Val {
        return true
    }
    if val < node.Val {
        return searchNode(node.Left, val)
    }
    return searchNode(node.Right, val)
}

// In-order traversal (sorted output) - O(n)
func inOrder(node *TreeNode) {
    if node == nil {
        return
    }
    inOrder(node.Left)
    fmt.Printf("%d ", node.Val)
    inOrder(node.Right)
}

// Delete node
func deleteNode(node *TreeNode, val int) *TreeNode {
    if node == nil {
        return nil
    }
    if val < node.Val {
        node.Left = deleteNode(node.Left, val)
    } else if val > node.Val {
        node.Right = deleteNode(node.Right, val)
    } else {
        // Node found
        if node.Left == nil {
            return node.Right
        }
        if node.Right == nil {
            return node.Left
        }
        // Two children: find in-order successor (smallest in right subtree)
        minNode := node.Right
        for minNode.Left != nil {
            minNode = minNode.Left
        }
        node.Val = minNode.Val
        node.Right = deleteNode(node.Right, minNode.Val)
    }
    return node
}

// BFS level-order traversal
func levelOrder(root *TreeNode) [][]int {
    if root == nil {
        return nil
    }
    var result [][]int
    queue := []*TreeNode{root}
    for len(queue) > 0 {
        levelSize := len(queue)
        var level []int
        for i := 0; i < levelSize; i++ {
            node := queue[0]
            queue = queue[1:]
            level = append(level, node.Val)
            if node.Left != nil {
                queue = append(queue, node.Left)
            }
            if node.Right != nil {
                queue = append(queue, node.Right)
            }
        }
        result = append(result, level)
    }
    return result
}

func main() {
    bst := &BST{}
    for _, v := range []int{8, 3, 10, 1, 6, 14, 4, 7, 13} {
        bst.Insert(v)
    }
    inOrder(bst.Root) // 1 3 4 6 7 8 10 13 14
    fmt.Println()
    fmt.Println("Search 6:", bst.Search(6))   // true
    fmt.Println("Search 99:", bst.Search(99)) // false
    fmt.Println("Levels:", levelOrder(bst.Root))
}
```

## Heaps
```
heap:
  what: Complete binary tree where parent is greater (max-heap) or smaller (min-heap) than children
  types:
    min_heap: Root is the smallest element
    max_heap: Root is the largest element

  time_complexity:
    insert: O(log n)       # add at bottom, bubble up
    extract_min_max: O(log n)  # remove root, bubble down
    peek_min_max: O(1)     # just return root
    build_heap: O(n)       # heapify an array
    search: O(n)           # not optimized for search

  space_complexity: O(n)

  implementation: Usually stored as an array
    parent: (i - 1) / 2
    left_child: 2*i + 1
    right_child: 2*i + 2

  when_to_use:
    - Priority queues
    - Find kth largest/smallest element
    - Merge k sorted lists
    - Heap sort
    - Median of stream
    - Dijkstra's algorithm
```

### Go Implementation
```go
package main

import (
    "container/heap"
    "fmt"
)

// MinHeap using Go's heap interface
type MinHeap []int

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *MinHeap) Push(x interface{}) {
    *h = append(*h, x.(int))
}

func (h *MinHeap) Pop() interface{} {
    old := *h
    n := len(old)
    x := old[n-1]
    *h = old[:n-1]
    return x
}

// Find kth largest element - O(n log k)
func findKthLargest(nums []int, k int) int {
    h := &MinHeap{}
    heap.Init(h)
    for _, num := range nums {
        heap.Push(h, num)
        if h.Len() > k {
            heap.Pop(h)
        }
    }
    return heap.Pop(h).(int)
}

func main() {
    h := &MinHeap{}
    heap.Init(h)

    heap.Push(h, 5)
    heap.Push(h, 2)
    heap.Push(h, 8)
    heap.Push(h, 1)

    for h.Len() > 0 {
        fmt.Println(heap.Pop(h)) // 1, 2, 5, 8
    }

    nums := []int{3, 2, 1, 5, 6, 4}
    fmt.Println("3rd largest:", findKthLargest(nums, 3)) // 4
}
```

## Graphs
```
graph:
  what: Set of vertices (nodes) connected by edges
  types:
    directed: Edges have direction (A -> B)
    undirected: Edges go both ways (A -- B)
    weighted: Edges have a cost/weight
    unweighted: All edges have equal cost
    cyclic: Contains at least one cycle
    acyclic: No cycles (DAG = Directed Acyclic Graph)

  representations:
    adjacency_list:
      what: Map of vertex to list of its neighbors
      space: O(V + E)
      best_for: Sparse graphs
    adjacency_matrix:
      what: 2D array where matrix[i][j] = 1 if edge exists
      space: O(V^2)
      best_for: Dense graphs, quick edge lookup

  time_complexity_adjacency_list:
    add_vertex: O(1)
    add_edge: O(1)
    remove_edge: O(E)
    BFS_DFS: O(V + E)
    find_edge: O(V)

  common_algorithms:
    BFS: Shortest path in unweighted graph
    DFS: Cycle detection, topological sort, connected components
    Dijkstra: Shortest path in weighted graph (no negative edges)
    Bellman_Ford: Shortest path with negative edges
    Topological_Sort: Order tasks with dependencies (DAG only)
    Kruskal_Prim: Minimum spanning tree

  when_to_use:
    - Social networks (friends, followers)
    - Maps and navigation
    - Dependency resolution
    - Network routing
    - Recommendation engines
```

### Go Implementation
```go
package main

import "fmt"

// Adjacency list graph
type Graph struct {
    adjacency map[int][]int
    directed  bool
}

func NewGraph(directed bool) *Graph {
    return &Graph{
        adjacency: make(map[int][]int),
        directed:  directed,
    }
}

func (g *Graph) AddEdge(from, to int) {
    g.adjacency[from] = append(g.adjacency[from], to)
    if !g.directed {
        g.adjacency[to] = append(g.adjacency[to], from)
    }
}

// BFS - O(V + E)
func (g *Graph) BFS(start int) []int {
    visited := make(map[int]bool)
    queue := []int{start}
    visited[start] = true
    var result []int

    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]
        result = append(result, node)

        for _, neighbor := range g.adjacency[node] {
            if !visited[neighbor] {
                visited[neighbor] = true
                queue = append(queue, neighbor)
            }
        }
    }
    return result
}

// DFS - O(V + E)
func (g *Graph) DFS(start int) []int {
    visited := make(map[int]bool)
    var result []int
    g.dfsHelper(start, visited, &result)
    return result
}

func (g *Graph) dfsHelper(node int, visited map[int]bool, result *[]int) {
    visited[node] = true
    *result = append(*result, node)
    for _, neighbor := range g.adjacency[node] {
        if !visited[neighbor] {
            g.dfsHelper(neighbor, visited, result)
        }
    }
}

// Detect cycle in directed graph
func (g *Graph) HasCycle() bool {
    visited := make(map[int]bool)
    inStack := make(map[int]bool)

    for node := range g.adjacency {
        if !visited[node] {
            if g.hasCycleDFS(node, visited, inStack) {
                return true
            }
        }
    }
    return false
}

func (g *Graph) hasCycleDFS(node int, visited, inStack map[int]bool) bool {
    visited[node] = true
    inStack[node] = true

    for _, neighbor := range g.adjacency[node] {
        if !visited[neighbor] {
            if g.hasCycleDFS(neighbor, visited, inStack) {
                return true
            }
        } else if inStack[neighbor] {
            return true
        }
    }
    inStack[node] = false
    return false
}

// Topological Sort (Kahn's algorithm - BFS-based)
func (g *Graph) TopologicalSort() []int {
    inDegree := make(map[int]int)
    for node := range g.adjacency {
        if _, ok := inDegree[node]; !ok {
            inDegree[node] = 0
        }
        for _, neighbor := range g.adjacency[node] {
            inDegree[neighbor]++
        }
    }

    var queue []int
    for node, degree := range inDegree {
        if degree == 0 {
            queue = append(queue, node)
        }
    }

    var result []int
    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]
        result = append(result, node)

        for _, neighbor := range g.adjacency[node] {
            inDegree[neighbor]--
            if inDegree[neighbor] == 0 {
                queue = append(queue, neighbor)
            }
        }
    }
    return result
}

func main() {
    g := NewGraph(false) // undirected
    g.AddEdge(0, 1)
    g.AddEdge(0, 2)
    g.AddEdge(1, 3)
    g.AddEdge(2, 4)

    fmt.Println("BFS:", g.BFS(0)) // [0 1 2 3 4]
    fmt.Println("DFS:", g.DFS(0)) // [0 1 3 2 4]

    dag := NewGraph(true) // directed
    dag.AddEdge(5, 2)
    dag.AddEdge(5, 0)
    dag.AddEdge(4, 0)
    dag.AddEdge(4, 1)
    dag.AddEdge(2, 3)
    dag.AddEdge(3, 1)
    fmt.Println("Topological Sort:", dag.TopologicalSort())
}
```

## Tries
```
trie:
  what: Tree-like structure for storing strings, where each node represents a character
  also_called: Prefix tree
  properties:
    - Root is empty
    - Each path from root to a marked node represents a word
    - Common prefixes share the same path

  time_complexity:
    insert: O(m)    # m = length of word
    search: O(m)
    prefix_search: O(m)
    delete: O(m)

  space_complexity: O(alphabet_size * m * n)  # n = number of words

  when_to_use:
    - Autocomplete / type-ahead
    - Spell checkers
    - IP routing (longest prefix match)
    - Word games (Scrabble, Boggle)
    - Dictionary implementation
    - Prefix-based searching
```

### Go Implementation
```go
package main

import "fmt"

type TrieNode struct {
    Children map[rune]*TrieNode
    IsEnd    bool
}

type Trie struct {
    Root *TrieNode
}

func NewTrie() *Trie {
    return &Trie{Root: &TrieNode{Children: make(map[rune]*TrieNode)}}
}

// Insert - O(m)
func (t *Trie) Insert(word string) {
    node := t.Root
    for _, ch := range word {
        if _, ok := node.Children[ch]; !ok {
            node.Children[ch] = &TrieNode{Children: make(map[rune]*TrieNode)}
        }
        node = node.Children[ch]
    }
    node.IsEnd = true
}

// Search exact word - O(m)
func (t *Trie) Search(word string) bool {
    node := t.findNode(word)
    return node != nil && node.IsEnd
}

// StartsWith - check if any word has this prefix - O(m)
func (t *Trie) StartsWith(prefix string) bool {
    return t.findNode(prefix) != nil
}

func (t *Trie) findNode(prefix string) *TrieNode {
    node := t.Root
    for _, ch := range prefix {
        if _, ok := node.Children[ch]; !ok {
            return nil
        }
        node = node.Children[ch]
    }
    return node
}

// Autocomplete - find all words with given prefix
func (t *Trie) Autocomplete(prefix string) []string {
    node := t.findNode(prefix)
    if node == nil {
        return nil
    }
    var results []string
    t.collectWords(node, prefix, &results)
    return results
}

func (t *Trie) collectWords(node *TrieNode, prefix string, results *[]string) {
    if node.IsEnd {
        *results = append(*results, prefix)
    }
    for ch, child := range node.Children {
        t.collectWords(child, prefix+string(ch), results)
    }
}

func main() {
    trie := NewTrie()
    words := []string{"apple", "app", "application", "apt", "bat", "batch"}
    for _, w := range words {
        trie.Insert(w)
    }

    fmt.Println("Search 'app':", trie.Search("app"))           // true
    fmt.Println("Search 'api':", trie.Search("api"))           // false
    fmt.Println("StartsWith 'app':", trie.StartsWith("app"))   // true
    fmt.Println("Autocomplete 'app':", trie.Autocomplete("app"))
    // [app apple application]
}
```

## Cheat Sheet
```
comparison:
  structure:        insert      search     delete     space    notes
  array:            O(n)        O(n)       O(n)       O(n)     O(1) access by index
  sorted_array:     O(n)        O(log n)   O(n)       O(n)     Binary search
  linked_list:      O(1) head   O(n)       O(n)       O(n)     O(1) if node known
  stack:            O(1)        O(n)       O(1) top   O(n)     LIFO
  queue:            O(1)        O(n)       O(1) front O(n)     FIFO
  hash_map:         O(1) avg    O(1) avg   O(1) avg   O(n)     Worst case O(n)
  BST:              O(log n)    O(log n)   O(log n)   O(n)     Worst case O(n) if skewed
  AVL_tree:         O(log n)    O(log n)   O(log n)   O(n)     Always balanced
  heap:             O(log n)    O(n)       O(log n)   O(n)     O(1) min/max access
  trie:             O(m)        O(m)       O(m)       O(a*m*n) m=word len, a=alphabet
  graph_adj_list:   O(1)        O(V)       O(E)       O(V+E)   BFS/DFS = O(V+E)

picking_the_right_one:
  need_fast_lookup_by_key: Hash Map
  need_sorted_data: BST / AVL Tree
  need_min_or_max: Heap
  need_FIFO: Queue
  need_LIFO: Stack
  need_prefix_search: Trie
  need_relationships: Graph
  need_fast_index_access: Array
  need_frequent_insert_delete: Linked List
```
