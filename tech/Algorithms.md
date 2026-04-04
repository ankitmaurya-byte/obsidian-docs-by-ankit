# Algorithms

## What are Algorithms
```
overview:
  definition: Step-by-step procedure to solve a problem or perform a computation
  key_concepts:
    - Correctness: Does it produce the right output for all valid inputs
    - Efficiency: How fast does it run (time) and how much memory does it use (space)
    - Scalability: How does performance change as input grows
  analysis:
    time_complexity: How many operations relative to input size
    space_complexity: How much extra memory relative to input size
    big_o: Upper bound on growth rate (worst case)
```

## Big O Notation
```
big_o:
  what: Describes how time/space grows as input size (n) grows
  focus: Worst-case scenario, drop constants and lower-order terms

  common_complexities_fastest_to_slowest:
    O(1):       Constant - hash map lookup, array index access
    O(log n):   Logarithmic - binary search, balanced BST ops
    O(n):       Linear - single loop through array
    O(n log n): Linearithmic - merge sort, heap sort
    O(n^2):     Quadratic - nested loops, bubble sort
    O(2^n):     Exponential - recursive subsets, brute force
    O(n!):      Factorial - permutations

  rules:
    drop_constants: "O(2n) = O(n), O(500) = O(1)"
    drop_lower_terms: "O(n^2 + n) = O(n^2)"
    different_inputs: "Two arrays = O(a + b) not O(n)"
    multiply_nested: "Nested loops = O(n * m)"

  space_complexity:
    what: Extra memory used beyond the input
    examples:
      O(1): Swapping variables, constant extra variables
      O(n): Creating a copy of the array, hash map of n elements
      O(n^2): 2D matrix of size n
    note: Recursive calls use O(depth) stack space
```

## Sorting Algorithms

### Bubble Sort
```
bubble_sort:
  what: Repeatedly swap adjacent elements if they are in wrong order
  time: O(n^2) average and worst, O(n) best (already sorted)
  space: O(1)
  stable: Yes
  when_to_use: Never in production, only for learning
```

```go
func bubbleSort(arr []int) {
    n := len(arr)
    for i := 0; i < n-1; i++ {
        swapped := false
        for j := 0; j < n-i-1; j++ {
            if arr[j] > arr[j+1] {
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = true
            }
        }
        if !swapped {
            break // already sorted
        }
    }
}
```

### Merge Sort
```
merge_sort:
  what: Divide array in half, sort each half, merge sorted halves
  approach: Divide and conquer
  time: O(n log n) always
  space: O(n) for the temporary arrays
  stable: Yes
  when_to_use:
    - Need guaranteed O(n log n)
    - Need stable sort
    - Sorting linked lists (no random access needed)
    - External sorting (data doesn't fit in memory)
```

```go
func mergeSort(arr []int) []int {
    if len(arr) <= 1 {
        return arr
    }
    mid := len(arr) / 2
    left := mergeSort(arr[:mid])
    right := mergeSort(arr[mid:])
    return merge(left, right)
}

func merge(left, right []int) []int {
    result := make([]int, 0, len(left)+len(right))
    i, j := 0, 0
    for i < len(left) && j < len(right) {
        if left[i] <= right[j] {
            result = append(result, left[i])
            i++
        } else {
            result = append(result, right[j])
            j++
        }
    }
    result = append(result, left[i:]...)
    result = append(result, right[j:]...)
    return result
}
```

### Quick Sort
```
quick_sort:
  what: Pick a pivot, partition array so smaller elements go left, larger go right, recurse
  approach: Divide and conquer
  time: O(n log n) average, O(n^2) worst (bad pivot)
  space: O(log n) average (call stack)
  stable: No
  when_to_use:
    - General purpose sorting (fastest in practice)
    - In-place sorting preferred
    - Cache-friendly (better locality than merge sort)
  pivot_selection:
    - Last element (simple)
    - Random element (avoids worst case)
    - Median of three (first, middle, last)
```

```go
func quickSort(arr []int, low, high int) {
    if low < high {
        pivot := partition(arr, low, high)
        quickSort(arr, low, pivot-1)
        quickSort(arr, pivot+1, high)
    }
}

func partition(arr []int, low, high int) int {
    pivot := arr[high]
    i := low - 1
    for j := low; j < high; j++ {
        if arr[j] < pivot {
            i++
            arr[i], arr[j] = arr[j], arr[i]
        }
    }
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i + 1
}
```

### Heap Sort
```
heap_sort:
  what: Build a max heap from array, repeatedly extract max to build sorted array
  time: O(n log n) always
  space: O(1)
  stable: No
  when_to_use:
    - Need guaranteed O(n log n) with O(1) space
    - Memory is constrained
```

```go
func heapSort(arr []int) {
    n := len(arr)

    // Build max heap - O(n)
    for i := n/2 - 1; i >= 0; i-- {
        heapify(arr, n, i)
    }

    // Extract elements from heap one by one
    for i := n - 1; i > 0; i-- {
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)
    }
}

func heapify(arr []int, n, i int) {
    largest := i
    left := 2*i + 1
    right := 2*i + 2

    if left < n && arr[left] > arr[largest] {
        largest = left
    }
    if right < n && arr[right] > arr[largest] {
        largest = right
    }
    if largest != i {
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)
    }
}
```

### Sorting Comparison
```
sorting_comparison:
  algorithm:     best        average     worst       space    stable
  bubble_sort:   O(n)        O(n^2)      O(n^2)      O(1)     Yes
  merge_sort:    O(n log n)  O(n log n)  O(n log n)  O(n)     Yes
  quick_sort:    O(n log n)  O(n log n)  O(n^2)      O(log n) No
  heap_sort:     O(n log n)  O(n log n)  O(n log n)  O(1)     No

  go_standard_library: sort.Slice uses introsort (quicksort + heapsort + insertion sort)
```

## Searching Algorithms

### Binary Search
```
binary_search:
  what: Search sorted array by repeatedly dividing search interval in half
  precondition: Array must be sorted
  time: O(log n)
  space: O(1) iterative, O(log n) recursive

  pattern:
    1: Set low = 0, high = len-1
    2: Find mid = (low + high) / 2
    3: If target == arr[mid], found
    4: If target < arr[mid], search left half
    5: If target > arr[mid], search right half
    6: Repeat until low > high

  when_to_use:
    - Sorted array search
    - Finding boundaries (first/last occurrence)
    - Search space problems (find minimum that satisfies condition)
    - Rotated sorted array problems
```

```go
// Standard binary search
func binarySearch(arr []int, target int) int {
    low, high := 0, len(arr)-1
    for low <= high {
        mid := low + (high-low)/2 // avoid overflow
        if arr[mid] == target {
            return mid
        }
        if arr[mid] < target {
            low = mid + 1
        } else {
            high = mid - 1
        }
    }
    return -1 // not found
}

// Find first occurrence (left boundary)
func findFirst(arr []int, target int) int {
    low, high := 0, len(arr)-1
    result := -1
    for low <= high {
        mid := low + (high-low)/2
        if arr[mid] == target {
            result = mid
            high = mid - 1 // keep searching left
        } else if arr[mid] < target {
            low = mid + 1
        } else {
            high = mid - 1
        }
    }
    return result
}

// Binary search on answer space
// Example: minimum capacity to ship packages in D days
func shipWithinDays(weights []int, days int) int {
    low, high := 0, 0
    for _, w := range weights {
        if w > low {
            low = w
        }
        high += w
    }

    for low < high {
        mid := low + (high-low)/2
        if canShip(weights, days, mid) {
            high = mid
        } else {
            low = mid + 1
        }
    }
    return low
}

func canShip(weights []int, days, capacity int) bool {
    daysNeeded, currentLoad := 1, 0
    for _, w := range weights {
        if currentLoad+w > capacity {
            daysNeeded++
            currentLoad = 0
        }
        currentLoad += w
    }
    return daysNeeded <= days
}
```

### BFS (Breadth-First Search)
```
bfs:
  what: Explore all neighbors at current depth before moving to next depth
  data_structure: Queue
  time: O(V + E) for graphs, O(n) for trees
  space: O(V) for the queue

  when_to_use:
    - Shortest path in unweighted graph
    - Level-order traversal of tree
    - Finding connected components
    - Minimum steps problems
```

```go
// BFS shortest path in unweighted graph
func bfsShortestPath(graph map[int][]int, start, end int) int {
    if start == end {
        return 0
    }
    visited := make(map[int]bool)
    queue := []int{start}
    visited[start] = true
    distance := 0

    for len(queue) > 0 {
        distance++
        levelSize := len(queue)
        for i := 0; i < levelSize; i++ {
            node := queue[0]
            queue = queue[1:]
            for _, neighbor := range graph[node] {
                if neighbor == end {
                    return distance
                }
                if !visited[neighbor] {
                    visited[neighbor] = true
                    queue = append(queue, neighbor)
                }
            }
        }
    }
    return -1 // not reachable
}

// BFS on a grid (common pattern)
func bfsGrid(grid [][]int, startR, startC int) int {
    rows, cols := len(grid), len(grid[0])
    directions := [][2]int{{0, 1}, {0, -1}, {1, 0}, {-1, 0}}
    visited := make([][]bool, rows)
    for i := range visited {
        visited[i] = make([]bool, cols)
    }

    queue := [][2]int{{startR, startC}}
    visited[startR][startC] = true
    steps := 0

    for len(queue) > 0 {
        levelSize := len(queue)
        for i := 0; i < levelSize; i++ {
            cell := queue[0]
            queue = queue[1:]
            r, c := cell[0], cell[1]

            for _, d := range directions {
                nr, nc := r+d[0], c+d[1]
                if nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                    !visited[nr][nc] && grid[nr][nc] != 1 {
                    visited[nr][nc] = true
                    queue = append(queue, [2]int{nr, nc})
                }
            }
        }
        steps++
    }
    return steps
}
```

### DFS (Depth-First Search)
```
dfs:
  what: Explore as deep as possible along a branch before backtracking
  data_structure: Stack (or recursion call stack)
  time: O(V + E) for graphs, O(n) for trees
  space: O(V) for the call stack

  when_to_use:
    - Cycle detection
    - Topological sorting
    - Path finding (all paths, not shortest)
    - Connected components
    - Backtracking problems
    - Tree traversals (in-order, pre-order, post-order)
```

```go
// DFS on graph - iterative with stack
func dfsIterative(graph map[int][]int, start int) []int {
    visited := make(map[int]bool)
    stack := []int{start}
    var result []int

    for len(stack) > 0 {
        node := stack[len(stack)-1]
        stack = stack[:len(stack)-1]

        if visited[node] {
            continue
        }
        visited[node] = true
        result = append(result, node)

        for _, neighbor := range graph[node] {
            if !visited[neighbor] {
                stack = append(stack, neighbor)
            }
        }
    }
    return result
}

// DFS on grid - count islands (classic problem)
func numIslands(grid [][]byte) int {
    if len(grid) == 0 {
        return 0
    }
    rows, cols := len(grid), len(grid[0])
    count := 0

    var dfs func(r, c int)
    dfs = func(r, c int) {
        if r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] == '0' {
            return
        }
        grid[r][c] = '0' // mark visited
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)
    }

    for r := 0; r < rows; r++ {
        for c := 0; c < cols; c++ {
            if grid[r][c] == '1' {
                count++
                dfs(r, c)
            }
        }
    }
    return count
}
```

## Dynamic Programming
```
dynamic_programming:
  what: Break problem into overlapping subproblems, solve each once, store results
  key_properties:
    optimal_substructure: Optimal solution contains optimal solutions to subproblems
    overlapping_subproblems: Same subproblems solved multiple times

  approaches:
    top_down_memoization:
      what: Recursive + cache results
      flow: Start from the original problem, break down, cache
    bottom_up_tabulation:
      what: Build solution iteratively from smallest subproblems
      flow: Start from base cases, build up to answer

  steps_to_solve:
    1: Define the subproblem (what does dp[i] represent?)
    2: Find the recurrence relation (how does dp[i] relate to smaller subproblems?)
    3: Identify base cases
    4: Determine computation order (bottom-up) or add memoization (top-down)
    5: Optimize space if possible

  common_patterns:
    - 0/1 Knapsack
    - Longest Common Subsequence
    - Longest Increasing Subsequence
    - Coin Change
    - Grid paths
    - String editing (edit distance)
    - Fibonacci variants
```

```go
// Fibonacci - top-down memoization
func fibMemo(n int, memo map[int]int) int {
    if n <= 1 {
        return n
    }
    if val, ok := memo[n]; ok {
        return val
    }
    memo[n] = fibMemo(n-1, memo) + fibMemo(n-2, memo)
    return memo[n]
}

// Fibonacci - bottom-up tabulation
func fibTab(n int) int {
    if n <= 1 {
        return n
    }
    dp := make([]int, n+1)
    dp[0], dp[1] = 0, 1
    for i := 2; i <= n; i++ {
        dp[i] = dp[i-1] + dp[i-2]
    }
    return dp[n]
}

// Fibonacci - space optimized O(1)
func fibOptimized(n int) int {
    if n <= 1 {
        return n
    }
    prev, curr := 0, 1
    for i := 2; i <= n; i++ {
        prev, curr = curr, prev+curr
    }
    return curr
}

// Coin Change - minimum coins to make amount
func coinChange(coins []int, amount int) int {
    dp := make([]int, amount+1)
    for i := range dp {
        dp[i] = amount + 1 // impossible value
    }
    dp[0] = 0

    for i := 1; i <= amount; i++ {
        for _, coin := range coins {
            if coin <= i && dp[i-coin]+1 < dp[i] {
                dp[i] = dp[i-coin] + 1
            }
        }
    }

    if dp[amount] > amount {
        return -1
    }
    return dp[amount]
}

// Longest Common Subsequence
func longestCommonSubsequence(text1, text2 string) int {
    m, n := len(text1), len(text2)
    dp := make([][]int, m+1)
    for i := range dp {
        dp[i] = make([]int, n+1)
    }

    for i := 1; i <= m; i++ {
        for j := 1; j <= n; j++ {
            if text1[i-1] == text2[j-1] {
                dp[i][j] = dp[i-1][j-1] + 1
            } else {
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            }
        }
    }
    return dp[m][n]
}

// 0/1 Knapsack
func knapsack(weights, values []int, capacity int) int {
    n := len(weights)
    dp := make([][]int, n+1)
    for i := range dp {
        dp[i] = make([]int, capacity+1)
    }

    for i := 1; i <= n; i++ {
        for w := 0; w <= capacity; w++ {
            dp[i][w] = dp[i-1][w] // don't take item
            if weights[i-1] <= w {
                take := dp[i-1][w-weights[i-1]] + values[i-1]
                if take > dp[i][w] {
                    dp[i][w] = take
                }
            }
        }
    }
    return dp[n][capacity]
}

func max(a, b int) int {
    if a > b {
        return a
    }
    return b
}
```

## Greedy Algorithms
```
greedy:
  what: Make the locally optimal choice at each step, hoping for global optimum
  key_property: Greedy choice property - local optimum leads to global optimum
  warning: Does not always work, must prove correctness

  when_it_works:
    - Activity selection / interval scheduling
    - Huffman coding
    - Minimum spanning tree (Kruskal, Prim)
    - Dijkstra's shortest path
    - Fractional knapsack

  when_it_fails:
    - 0/1 Knapsack (need DP)
    - Coin change with arbitrary denominations (need DP)
    - Traveling salesman (NP-hard)
```

```go
// Activity Selection - max non-overlapping intervals
import "sort"

type Interval struct {
    Start, End int
}

func maxActivities(intervals []Interval) int {
    sort.Slice(intervals, func(i, j int) bool {
        return intervals[i].End < intervals[j].End
    })

    count := 1
    lastEnd := intervals[0].End
    for i := 1; i < len(intervals); i++ {
        if intervals[i].Start >= lastEnd {
            count++
            lastEnd = intervals[i].End
        }
    }
    return count
}

// Jump Game - can you reach the last index
func canJump(nums []int) bool {
    maxReach := 0
    for i := 0; i < len(nums); i++ {
        if i > maxReach {
            return false
        }
        if i+nums[i] > maxReach {
            maxReach = i + nums[i]
        }
    }
    return true
}
```

## Two Pointers
```
two_pointers:
  what: Use two pointers to traverse array/string from different positions
  variants:
    opposite_ends: One at start, one at end, move inward
    same_direction: Both from start, fast and slow
    two_arrays: One pointer per array

  time: Usually O(n)
  space: Usually O(1)

  when_to_use:
    - Sorted array problems (two sum in sorted array)
    - Palindrome checking
    - Removing duplicates
    - Container with most water
    - Linked list cycle detection (fast/slow)
    - Merging sorted arrays
```

```go
// Two Sum in sorted array - O(n)
func twoSumSorted(nums []int, target int) [2]int {
    left, right := 0, len(nums)-1
    for left < right {
        sum := nums[left] + nums[right]
        if sum == target {
            return [2]int{left, right}
        }
        if sum < target {
            left++
        } else {
            right--
        }
    }
    return [2]int{-1, -1}
}

// Remove duplicates from sorted array - O(n)
func removeDuplicates(nums []int) int {
    if len(nums) == 0 {
        return 0
    }
    slow := 0
    for fast := 1; fast < len(nums); fast++ {
        if nums[fast] != nums[slow] {
            slow++
            nums[slow] = nums[fast]
        }
    }
    return slow + 1
}

// Container with most water - O(n)
func maxArea(height []int) int {
    left, right := 0, len(height)-1
    maxWater := 0
    for left < right {
        h := min(height[left], height[right])
        water := h * (right - left)
        if water > maxWater {
            maxWater = water
        }
        if height[left] < height[right] {
            left++
        } else {
            right--
        }
    }
    return maxWater
}

// Linked list cycle detection - Floyd's algorithm
type ListNode struct {
    Val  int
    Next *ListNode
}

func hasCycle(head *ListNode) bool {
    slow, fast := head, head
    for fast != nil && fast.Next != nil {
        slow = slow.Next
        fast = fast.Next.Next
        if slow == fast {
            return true
        }
    }
    return false
}

func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}
```

## Sliding Window
```
sliding_window:
  what: Maintain a window (subarray/substring) that slides across the input
  types:
    fixed_size: Window size is given (e.g., max sum of k elements)
    variable_size: Window grows/shrinks based on condition

  time: Usually O(n)
  space: O(1) to O(k) depending on what you track

  pattern:
    1: Initialize window (start with first element or empty)
    2: Expand window by moving right pointer
    3: When condition violated, shrink by moving left pointer
    4: Track the answer at each valid state

  when_to_use:
    - Maximum/minimum sum subarray of size k
    - Longest substring without repeating characters
    - Minimum window substring
    - Count subarrays with at most k distinct elements
    - String anagram/permutation matching
```

```go
// Max sum subarray of size k - fixed window
func maxSumSubarray(arr []int, k int) int {
    windowSum := 0
    for i := 0; i < k; i++ {
        windowSum += arr[i]
    }
    maxSum := windowSum
    for i := k; i < len(arr); i++ {
        windowSum += arr[i] - arr[i-k] // slide: add right, remove left
        if windowSum > maxSum {
            maxSum = windowSum
        }
    }
    return maxSum
}

// Longest substring without repeating characters - variable window
func lengthOfLongestSubstring(s string) int {
    charIndex := make(map[byte]int)
    maxLen := 0
    left := 0

    for right := 0; right < len(s); right++ {
        if idx, ok := charIndex[s[right]]; ok && idx >= left {
            left = idx + 1
        }
        charIndex[s[right]] = right
        if right-left+1 > maxLen {
            maxLen = right - left + 1
        }
    }
    return maxLen
}

// Minimum window substring
func minWindow(s string, t string) string {
    need := make(map[byte]int)
    for i := 0; i < len(t); i++ {
        need[t[i]]++
    }

    have := make(map[byte]int)
    formed := 0
    required := len(need)
    left := 0
    minLen := len(s) + 1
    minStart := 0

    for right := 0; right < len(s); right++ {
        ch := s[right]
        have[ch]++
        if have[ch] == need[ch] {
            formed++
        }

        for formed == required {
            if right-left+1 < minLen {
                minLen = right - left + 1
                minStart = left
            }
            leftCh := s[left]
            have[leftCh]--
            if have[leftCh] < need[leftCh] {
                formed--
            }
            left++
        }
    }

    if minLen > len(s) {
        return ""
    }
    return s[minStart : minStart+minLen]
}
```

## Recursion
```
recursion:
  what: Function that calls itself to break a problem into smaller subproblems
  components:
    base_case: Condition to stop recursion (prevents infinite loop)
    recursive_case: Break problem down and call self
    return_value: Combine results from recursive calls

  thinking_framework:
    1: What is the simplest case (base case)?
    2: How can I break this into a smaller version of the same problem?
    3: How do I combine the result?

  common_pitfalls:
    - Missing or wrong base case (infinite recursion)
    - Stack overflow for deep recursion
    - Redundant computation (add memoization)

  tail_recursion:
    what: Recursive call is the last operation in function
    benefit: Compiler can optimize to iteration (Go does NOT optimize tail calls)
```

```go
// Power function - O(log n)
func power(base, exp int) int {
    if exp == 0 {
        return 1
    }
    if exp%2 == 0 {
        half := power(base, exp/2)
        return half * half
    }
    return base * power(base, exp-1)
}

// Generate all subsets (power set)
func subsets(nums []int) [][]int {
    var result [][]int
    var backtrack func(start int, current []int)
    backtrack = func(start int, current []int) {
        // Make a copy and add to result
        tmp := make([]int, len(current))
        copy(tmp, current)
        result = append(result, tmp)

        for i := start; i < len(nums); i++ {
            current = append(current, nums[i])
            backtrack(i+1, current)
            current = current[:len(current)-1] // backtrack
        }
    }
    backtrack(0, []int{})
    return result
}

// Generate all permutations
func permutations(nums []int) [][]int {
    var result [][]int
    var backtrack func(start int)
    backtrack = func(start int) {
        if start == len(nums) {
            tmp := make([]int, len(nums))
            copy(tmp, nums)
            result = append(result, tmp)
            return
        }
        for i := start; i < len(nums); i++ {
            nums[start], nums[i] = nums[i], nums[start]
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start]
        }
    }
    backtrack(0)
    return result
}
```

## Algorithm Selection Guide
```
selection_guide:
  problem_type:
    sorted_array_search: Binary Search - O(log n)
    shortest_path_unweighted: BFS - O(V + E)
    shortest_path_weighted: Dijkstra - O((V + E) log V)
    all_paths_or_cycle_detection: DFS - O(V + E)
    optimal_substructure_overlapping: Dynamic Programming
    local_choice_gives_global: Greedy
    generate_all_combinations: Backtracking / Recursion
    sorted_array_pair_sum: Two Pointers - O(n)
    subarray_substring_window: Sliding Window - O(n)
    need_sorted_output: Merge Sort or Quick Sort - O(n log n)
    top_k_elements: Heap - O(n log k)
    frequency_counting: Hash Map - O(n)

  optimization_tips:
    - If brute force is O(n^2), try two pointers or sliding window for O(n)
    - If brute force is O(2^n), try DP for O(n^2) or O(n*m)
    - If searching unsorted, consider sorting first for O(n log n) + O(log n)
    - If repeated lookups needed, precompute with hash map
```
