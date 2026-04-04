# DSA Patterns

## Overview
```
dsa_patterns:
  what: Reusable problem-solving templates that apply to many coding interview questions
  why_they_matter:
    - Most interview problems are variations of ~15 core patterns
    - Recognizing the pattern is 80% of solving the problem
    - Template code lets you focus on the problem-specific logic
  approach:
    1: Read the problem and identify constraints
    2: Map constraints to a known pattern
    3: Apply the template and customize
    4: Verify with edge cases
```

## Two Pointers

### Overview
```
two_pointers:
  what: Use two index variables to traverse a data structure, reducing nested loops
  types:
    opposite_direction: One pointer at start, one at end, move toward each other
    same_direction: Both start at beginning, fast pointer moves ahead (slow/fast)

  when_to_recognize:
    - Sorted array and need to find pair with target sum
    - Need to remove duplicates in-place
    - Palindrome checking
    - Linked list cycle detection
    - Partitioning problems

  time_complexity: O(n)
  space_complexity: O(1)
```

### Opposite Direction Template
```go
// Two Sum in sorted array - find two numbers that sum to target
func twoSumSorted(nums []int, target int) []int {
    left, right := 0, len(nums)-1
    for left < right {
        sum := nums[left] + nums[right]
        if sum == target {
            return []int{left, right}
        } else if sum < target {
            left++
        } else {
            right--
        }
    }
    return []int{-1, -1}
}

// Check if string is palindrome
func isPalindrome(s string) bool {
    left, right := 0, len(s)-1
    for left < right {
        if s[left] != s[right] {
            return false
        }
        left++
        right--
    }
    return true
}

// Container With Most Water (LC 11)
func maxArea(height []int) int {
    left, right := 0, len(height)-1
    maxWater := 0
    for left < right {
        w := right - left
        h := min(height[left], height[right])
        maxWater = max(maxWater, w*h)
        if height[left] < height[right] {
            left++
        } else {
            right--
        }
    }
    return maxWater
}
```

### Same Direction (Slow/Fast) Template
```go
// Remove duplicates from sorted array in-place (LC 26)
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

// Linked list cycle detection (Floyd's Tortoise and Hare)
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

// Find middle of linked list
func findMiddle(head *ListNode) *ListNode {
    slow, fast := head, head
    for fast != nil && fast.Next != nil {
        slow = slow.Next
        fast = fast.Next.Next
    }
    return slow
}
```

### Example Problems
```
example_problems:
  1_two_sum_ii: "Sorted array, find pair summing to target -> opposite direction"
  2_three_sum: "Find all triplets summing to 0 -> fix one, two pointers on rest"
  3_trapping_rain_water: "Find water trapped -> opposite direction with max tracking"
```

### Three Sum Solution
```go
// Three Sum (LC 15) - find all unique triplets that sum to 0
func threeSum(nums []int) [][]int {
    sort.Ints(nums)
    result := [][]int{}
    for i := 0; i < len(nums)-2; i++ {
        if i > 0 && nums[i] == nums[i-1] {
            continue // skip duplicate
        }
        left, right := i+1, len(nums)-1
        for left < right {
            sum := nums[i] + nums[left] + nums[right]
            if sum == 0 {
                result = append(result, []int{nums[i], nums[left], nums[right]})
                for left < right && nums[left] == nums[left+1] {
                    left++
                }
                for left < right && nums[right] == nums[right-1] {
                    right--
                }
                left++
                right--
            } else if sum < 0 {
                left++
            } else {
                right--
            }
        }
    }
    return result
}
```

## Sliding Window

### Overview
```
sliding_window:
  what: Maintain a window (subarray/substring) that slides through data
  types:
    fixed_size: Window size is given, slide one element at a time
    variable_size: Window expands/shrinks based on condition

  when_to_recognize:
    - "Subarray/substring of size k"
    - "Longest/shortest subarray with condition"
    - "Maximum sum subarray of size k"
    - Contiguous sequence problems

  time_complexity: O(n)
  space_complexity: O(1) or O(k) depending on what you track
```

### Fixed Size Window
```go
// Maximum sum subarray of size k
func maxSumSubarray(nums []int, k int) int {
    windowSum := 0
    for i := 0; i < k; i++ {
        windowSum += nums[i]
    }
    maxSum := windowSum
    for i := k; i < len(nums); i++ {
        windowSum += nums[i] - nums[i-k] // slide: add right, remove left
        maxSum = max(maxSum, windowSum)
    }
    return maxSum
}

// Find all anagrams in a string (LC 438)
func findAnagrams(s string, p string) []int {
    if len(s) < len(p) {
        return nil
    }
    result := []int{}
    pCount := [26]int{}
    sCount := [26]int{}
    for i := 0; i < len(p); i++ {
        pCount[p[i]-'a']++
        sCount[s[i]-'a']++
    }
    if pCount == sCount {
        result = append(result, 0)
    }
    for i := len(p); i < len(s); i++ {
        sCount[s[i]-'a']++
        sCount[s[i-len(p)]-'a']--
        if pCount == sCount {
            result = append(result, i-len(p)+1)
        }
    }
    return result
}
```

### Variable Size Window
```go
// Longest substring without repeating characters (LC 3)
func lengthOfLongestSubstring(s string) int {
    charIndex := make(map[byte]int)
    maxLen := 0
    left := 0
    for right := 0; right < len(s); right++ {
        if idx, exists := charIndex[s[right]]; exists && idx >= left {
            left = idx + 1 // shrink window
        }
        charIndex[s[right]] = right
        maxLen = max(maxLen, right-left+1)
    }
    return maxLen
}

// Minimum window substring (LC 76)
func minWindow(s string, t string) string {
    if len(s) < len(t) {
        return ""
    }
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
        c := s[right]
        have[c]++
        if have[c] == need[c] {
            formed++
        }
        for formed == required {
            if right-left+1 < minLen {
                minLen = right - left + 1
                minStart = left
            }
            have[s[left]]--
            if have[s[left]] < need[s[left]] {
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

// Smallest subarray with sum >= target (LC 209)
func minSubArrayLen(target int, nums []int) int {
    left, sum := 0, 0
    minLen := len(nums) + 1
    for right := 0; right < len(nums); right++ {
        sum += nums[right]
        for sum >= target {
            minLen = min(minLen, right-left+1)
            sum -= nums[left]
            left++
        }
    }
    if minLen > len(nums) {
        return 0
    }
    return minLen
}
```

## Binary Search

### Overview
```
binary_search:
  what: Eliminate half the search space at each step
  types:
    on_sorted_array: Classic search for target in sorted data
    on_answer_space: Binary search on the answer itself (min/max optimization)

  when_to_recognize:
    - Sorted array or rotated sorted array
    - "Find minimum/maximum that satisfies condition"
    - "Find first/last occurrence"
    - Monotonic function (if f(x) is true, f(x+1) is also true)

  time_complexity: O(log n)
  space_complexity: O(1) iterative, O(log n) recursive
```

### Standard Binary Search
```go
// Classic binary search
func binarySearch(nums []int, target int) int {
    left, right := 0, len(nums)-1
    for left <= right {
        mid := left + (right-left)/2 // avoid overflow
        if nums[mid] == target {
            return mid
        } else if nums[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    return -1
}

// Find first occurrence (leftmost)
func firstOccurrence(nums []int, target int) int {
    left, right := 0, len(nums)-1
    result := -1
    for left <= right {
        mid := left + (right-left)/2
        if nums[mid] == target {
            result = mid
            right = mid - 1 // keep searching left
        } else if nums[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    return result
}

// Find last occurrence (rightmost)
func lastOccurrence(nums []int, target int) int {
    left, right := 0, len(nums)-1
    result := -1
    for left <= right {
        mid := left + (right-left)/2
        if nums[mid] == target {
            result = mid
            left = mid + 1 // keep searching right
        } else if nums[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    return result
}

// Search in rotated sorted array (LC 33)
func searchRotated(nums []int, target int) int {
    left, right := 0, len(nums)-1
    for left <= right {
        mid := left + (right-left)/2
        if nums[mid] == target {
            return mid
        }
        if nums[left] <= nums[mid] { // left half is sorted
            if nums[left] <= target && target < nums[mid] {
                right = mid - 1
            } else {
                left = mid + 1
            }
        } else { // right half is sorted
            if nums[mid] < target && target <= nums[right] {
                left = mid + 1
            } else {
                right = mid - 1
            }
        }
    }
    return -1
}
```

### Binary Search on Answer Space
```go
// Koko eating bananas (LC 875) - find minimum speed to eat all bananas in h hours
func minEatingSpeed(piles []int, h int) int {
    left, right := 1, 0
    for _, p := range piles {
        if p > right {
            right = p
        }
    }
    canFinish := func(speed int) bool {
        hours := 0
        for _, p := range piles {
            hours += (p + speed - 1) / speed // ceiling division
        }
        return hours <= h
    }
    for left < right {
        mid := left + (right-left)/2
        if canFinish(mid) {
            right = mid // try smaller speed
        } else {
            left = mid + 1
        }
    }
    return left
}

// Split array largest sum (LC 410) - minimize the largest sum among m subarrays
func splitArray(nums []int, m int) int {
    left, right := 0, 0
    for _, n := range nums {
        if n > left {
            left = n
        }
        right += n
    }
    canSplit := func(maxSum int) bool {
        count, currSum := 1, 0
        for _, n := range nums {
            if currSum+n > maxSum {
                count++
                currSum = n
            } else {
                currSum += n
            }
        }
        return count <= m
    }
    for left < right {
        mid := left + (right-left)/2
        if canSplit(mid) {
            right = mid
        } else {
            left = mid + 1
        }
    }
    return left
}
```

## BFS / DFS

### Overview
```
bfs_dfs:
  what: Graph/tree traversal strategies
  bfs:
    approach: Level by level using a queue
    best_for: Shortest path in unweighted graphs, level-order problems
    time: O(V + E) for graphs, O(n) for trees
    space: O(V) for queue
  dfs:
    approach: Go as deep as possible before backtracking
    best_for: Path finding, cycle detection, connected components, tree problems
    time: O(V + E) for graphs, O(n) for trees
    space: O(V) for stack/recursion

  when_to_recognize:
    - "Find shortest path" -> BFS
    - "Find all paths / any path" -> DFS
    - "Level order" -> BFS
    - "Connected components" -> DFS
    - Matrix traversal (islands, flood fill) -> BFS or DFS
```

### BFS on Tree (Level Order)
```go
type TreeNode struct {
    Val   int
    Left  *TreeNode
    Right *TreeNode
}

// Level order traversal (LC 102)
func levelOrder(root *TreeNode) [][]int {
    if root == nil {
        return nil
    }
    result := [][]int{}
    queue := []*TreeNode{root}
    for len(queue) > 0 {
        levelSize := len(queue)
        level := make([]int, 0, levelSize)
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
```

### BFS on Matrix (Shortest Path)
```go
// Shortest path in binary matrix (LC 1091)
func shortestPathBinaryMatrix(grid [][]int) int {
    n := len(grid)
    if grid[0][0] == 1 || grid[n-1][n-1] == 1 {
        return -1
    }
    dirs := [][2]int{{0, 1}, {0, -1}, {1, 0}, {-1, 0},
        {1, 1}, {1, -1}, {-1, 1}, {-1, -1}}
    queue := [][2]int{{0, 0}}
    grid[0][0] = 1 // mark visited
    dist := 1
    for len(queue) > 0 {
        size := len(queue)
        for i := 0; i < size; i++ {
            r, c := queue[0][0], queue[0][1]
            queue = queue[1:]
            if r == n-1 && c == n-1 {
                return dist
            }
            for _, d := range dirs {
                nr, nc := r+d[0], c+d[1]
                if nr >= 0 && nr < n && nc >= 0 && nc < n && grid[nr][nc] == 0 {
                    grid[nr][nc] = 1
                    queue = append(queue, [2]int{nr, nc})
                }
            }
        }
        dist++
    }
    return -1
}
```

### DFS on Graph
```go
// Number of islands (LC 200)
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

// Clone graph (LC 133)
type Node struct {
    Val       int
    Neighbors []*Node
}

func cloneGraph(node *Node) *Node {
    if node == nil {
        return nil
    }
    visited := make(map[*Node]*Node)
    var dfs func(*Node) *Node
    dfs = func(n *Node) *Node {
        if clone, ok := visited[n]; ok {
            return clone
        }
        clone := &Node{Val: n.Val}
        visited[n] = clone
        for _, neighbor := range n.Neighbors {
            clone.Neighbors = append(clone.Neighbors, dfs(neighbor))
        }
        return clone
    }
    return dfs(node)
}
```

## Backtracking

### Overview
```
backtracking:
  what: Build solution incrementally, abandon paths that cannot lead to valid solution
  template:
    1: Make a choice
    2: Recurse with that choice
    3: Undo the choice (backtrack)

  when_to_recognize:
    - "Find all combinations/permutations/subsets"
    - "Generate all valid configurations"
    - "Constraint satisfaction (N-Queens, Sudoku)"
    - Problem asks for ALL solutions, not just count

  time_complexity: Usually exponential O(2^n) or O(n!)
  space_complexity: O(n) for recursion depth
```

### Subsets
```go
// All subsets (LC 78)
func subsets(nums []int) [][]int {
    result := [][]int{}
    current := []int{}
    var backtrack func(start int)
    backtrack = func(start int) {
        // make a copy and add to result
        temp := make([]int, len(current))
        copy(temp, current)
        result = append(result, temp)
        for i := start; i < len(nums); i++ {
            current = append(current, nums[i])
            backtrack(i + 1)
            current = current[:len(current)-1] // undo choice
        }
    }
    backtrack(0)
    return result
}

// Subsets II - with duplicates (LC 90)
func subsetsWithDup(nums []int) [][]int {
    sort.Ints(nums) // sort to handle duplicates
    result := [][]int{}
    current := []int{}
    var backtrack func(start int)
    backtrack = func(start int) {
        temp := make([]int, len(current))
        copy(temp, current)
        result = append(result, temp)
        for i := start; i < len(nums); i++ {
            if i > start && nums[i] == nums[i-1] {
                continue // skip duplicates
            }
            current = append(current, nums[i])
            backtrack(i + 1)
            current = current[:len(current)-1]
        }
    }
    backtrack(0)
    return result
}
```

### Permutations
```go
// All permutations (LC 46)
func permute(nums []int) [][]int {
    result := [][]int{}
    var backtrack func(start int)
    backtrack = func(start int) {
        if start == len(nums) {
            temp := make([]int, len(nums))
            copy(temp, nums)
            result = append(result, temp)
            return
        }
        for i := start; i < len(nums); i++ {
            nums[start], nums[i] = nums[i], nums[start]
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start] // undo
        }
    }
    backtrack(0)
    return result
}
```

### Combinations
```go
// Combinations of k numbers from 1..n (LC 77)
func combine(n int, k int) [][]int {
    result := [][]int{}
    current := []int{}
    var backtrack func(start int)
    backtrack = func(start int) {
        if len(current) == k {
            temp := make([]int, k)
            copy(temp, current)
            result = append(result, temp)
            return
        }
        // pruning: need k-len(current) more elements
        for i := start; i <= n-(k-len(current))+1; i++ {
            current = append(current, i)
            backtrack(i + 1)
            current = current[:len(current)-1]
        }
    }
    backtrack(1)
    return result
}

// Combination Sum - elements can be reused (LC 39)
func combinationSum(candidates []int, target int) [][]int {
    result := [][]int{}
    current := []int{}
    var backtrack func(start, remaining int)
    backtrack = func(start, remaining int) {
        if remaining == 0 {
            temp := make([]int, len(current))
            copy(temp, current)
            result = append(result, temp)
            return
        }
        for i := start; i < len(candidates); i++ {
            if candidates[i] > remaining {
                continue
            }
            current = append(current, candidates[i])
            backtrack(i, remaining-candidates[i]) // i, not i+1 (reuse allowed)
            current = current[:len(current)-1]
        }
    }
    backtrack(0, target)
    return result
}
```

## Dynamic Programming

### Overview
```
dynamic_programming:
  what: Break problem into overlapping subproblems, store results to avoid recomputation
  approaches:
    top_down: Recursive with memoization (cache results of subproblems)
    bottom_up: Iterative, build solution from smallest subproblems up
  key_concepts:
    optimal_substructure: Optimal solution contains optimal solutions to subproblems
    overlapping_subproblems: Same subproblems are solved multiple times

  when_to_recognize:
    - "Find minimum/maximum cost/path/count"
    - "How many ways to..."
    - "Is it possible to..."
    - Can be broken into smaller versions of same problem
    - Choices at each step affect future choices

  common_state_transitions:
    linear: "dp[i] depends on dp[i-1], dp[i-2], etc."
    two_dimensional: "dp[i][j] depends on dp[i-1][j], dp[i][j-1], etc."
    interval: "dp[i][j] depends on dp[i+1][j], dp[i][j-1], dp[i+1][j-1]"
```

### Top-Down Memoization Template
```go
// Fibonacci - top down
func fib(n int) int {
    memo := make(map[int]int)
    var solve func(n int) int
    solve = func(n int) int {
        if n <= 1 {
            return n
        }
        if v, ok := memo[n]; ok {
            return v
        }
        memo[n] = solve(n-1) + solve(n-2)
        return memo[n]
    }
    return solve(n)
}
```

### Bottom-Up Tabulation Template
```go
// Fibonacci - bottom up
func fib(n int) int {
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

// Space optimized - only need previous two values
func fibOptimized(n int) int {
    if n <= 1 {
        return n
    }
    prev2, prev1 := 0, 1
    for i := 2; i <= n; i++ {
        curr := prev1 + prev2
        prev2 = prev1
        prev1 = curr
    }
    return prev1
}
```

### Classic DP Problems
```go
// Coin Change (LC 322) - minimum coins to make amount
func coinChange(coins []int, amount int) int {
    dp := make([]int, amount+1)
    for i := range dp {
        dp[i] = amount + 1 // sentinel
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

// Longest Increasing Subsequence (LC 300)
func lengthOfLIS(nums []int) int {
    // O(n log n) using patience sorting
    tails := []int{}
    for _, num := range nums {
        pos := sort.SearchInts(tails, num)
        if pos == len(tails) {
            tails = append(tails, num)
        } else {
            tails[pos] = num
        }
    }
    return len(tails)
}

// 0/1 Knapsack
func knapsack(weights, values []int, capacity int) int {
    n := len(weights)
    dp := make([]int, capacity+1)
    for i := 0; i < n; i++ {
        for w := capacity; w >= weights[i]; w-- { // reverse to avoid reuse
            dp[w] = max(dp[w], dp[w-weights[i]]+values[i])
        }
    }
    return dp[capacity]
}
```

## Greedy

### Overview
```
greedy:
  what: Make locally optimal choice at each step, hoping for global optimum
  key_insight: Works when local optimal leads to global optimal (greedy choice property)

  when_to_recognize:
    - Interval scheduling / merging problems
    - "Minimum number of X to cover Y"
    - Sorting + greedy selection
    - Problem has greedy choice property + optimal substructure

  caution: Not all optimization problems can be solved greedily
  time_complexity: Usually O(n log n) due to sorting
```

### Interval Scheduling
```go
// Merge intervals (LC 56)
func merge(intervals [][]int) [][]int {
    sort.Slice(intervals, func(i, j int) bool {
        return intervals[i][0] < intervals[j][0]
    })
    result := [][]int{intervals[0]}
    for i := 1; i < len(intervals); i++ {
        last := result[len(result)-1]
        if intervals[i][0] <= last[1] { // overlapping
            last[1] = max(last[1], intervals[i][1])
        } else {
            result = append(result, intervals[i])
        }
    }
    return result
}

// Non-overlapping intervals / Activity Selection (LC 435)
// Minimum removals to make intervals non-overlapping
func eraseOverlapIntervals(intervals [][]int) int {
    sort.Slice(intervals, func(i, j int) bool {
        return intervals[i][1] < intervals[j][1] // sort by end time
    })
    count := 0
    end := intervals[0][1]
    for i := 1; i < len(intervals); i++ {
        if intervals[i][0] < end {
            count++ // overlap, remove this one
        } else {
            end = intervals[i][1]
        }
    }
    return count
}

// Jump Game (LC 55)
func canJump(nums []int) bool {
    maxReach := 0
    for i := 0; i < len(nums); i++ {
        if i > maxReach {
            return false
        }
        maxReach = max(maxReach, i+nums[i])
    }
    return true
}

// Jump Game II (LC 45) - minimum jumps
func jump(nums []int) int {
    jumps, curEnd, farthest := 0, 0, 0
    for i := 0; i < len(nums)-1; i++ {
        farthest = max(farthest, i+nums[i])
        if i == curEnd {
            jumps++
            curEnd = farthest
        }
    }
    return jumps
}
```

## Stack / Queue Tricks

### Overview
```
stack_queue_tricks:
  what: Use stack/queue properties to solve problems efficiently
  monotonic_stack:
    what: Stack that maintains elements in monotonic (increasing or decreasing) order
    use_for: Next greater/smaller element, histogram problems
  monotonic_queue:
    what: Deque maintaining monotonic order for sliding window max/min
    use_for: Sliding window maximum

  when_to_recognize:
    - "Next greater/smaller element"
    - "Sliding window maximum/minimum"
    - "Largest rectangle in histogram"
    - Valid parentheses / bracket matching
    - Expression evaluation

  time_complexity: O(n) - each element pushed and popped at most once
  space_complexity: O(n)
```

### Monotonic Stack
```go
// Next greater element (LC 496 variant)
// For each element, find the next element that is greater
func nextGreaterElement(nums []int) []int {
    n := len(nums)
    result := make([]int, n)
    for i := range result {
        result[i] = -1
    }
    stack := []int{} // stack of indices
    for i := 0; i < n; i++ {
        for len(stack) > 0 && nums[i] > nums[stack[len(stack)-1]] {
            idx := stack[len(stack)-1]
            stack = stack[:len(stack)-1]
            result[idx] = nums[i]
        }
        stack = append(stack, i)
    }
    return result
}

// Daily temperatures (LC 739) - days until warmer temperature
func dailyTemperatures(temperatures []int) []int {
    n := len(temperatures)
    result := make([]int, n)
    stack := []int{}
    for i := 0; i < n; i++ {
        for len(stack) > 0 && temperatures[i] > temperatures[stack[len(stack)-1]] {
            idx := stack[len(stack)-1]
            stack = stack[:len(stack)-1]
            result[idx] = i - idx
        }
        stack = append(stack, i)
    }
    return result
}

// Largest rectangle in histogram (LC 84)
func largestRectangleArea(heights []int) int {
    stack := []int{}
    maxArea := 0
    heights = append(heights, 0) // sentinel
    for i := 0; i < len(heights); i++ {
        for len(stack) > 0 && heights[i] < heights[stack[len(stack)-1]] {
            h := heights[stack[len(stack)-1]]
            stack = stack[:len(stack)-1]
            w := i
            if len(stack) > 0 {
                w = i - stack[len(stack)-1] - 1
            }
            maxArea = max(maxArea, h*w)
        }
        stack = append(stack, i)
    }
    return maxArea
}
```

### Sliding Window Maximum with Deque
```go
// Sliding window maximum (LC 239)
func maxSlidingWindow(nums []int, k int) []int {
    deque := []int{} // indices, front is always the max
    result := []int{}
    for i := 0; i < len(nums); i++ {
        // remove elements outside window
        for len(deque) > 0 && deque[0] < i-k+1 {
            deque = deque[1:]
        }
        // remove smaller elements from back
        for len(deque) > 0 && nums[deque[len(deque)-1]] < nums[i] {
            deque = deque[:len(deque)-1]
        }
        deque = append(deque, i)
        if i >= k-1 {
            result = append(result, nums[deque[0]])
        }
    }
    return result
}
```

## Prefix Sum

### Overview
```
prefix_sum:
  what: Precompute cumulative sums to answer range sum queries in O(1)
  formula: "prefixSum[i] = nums[0] + nums[1] + ... + nums[i-1]"
  range_sum: "sum(i, j) = prefixSum[j+1] - prefixSum[i]"

  when_to_recognize:
    - "Subarray sum equals k"
    - "Range sum query"
    - "Number of subarrays with sum = target"
    - Difference between cumulative values

  time_complexity: O(n) to build, O(1) per query
  space_complexity: O(n)
```

### Implementation
```go
// Build prefix sum
func buildPrefixSum(nums []int) []int {
    prefix := make([]int, len(nums)+1)
    for i := 0; i < len(nums); i++ {
        prefix[i+1] = prefix[i] + nums[i]
    }
    return prefix
    // rangeSum(i, j) = prefix[j+1] - prefix[i]
}

// Subarray sum equals K (LC 560)
func subarraySum(nums []int, k int) int {
    count := 0
    sum := 0
    prefixCount := map[int]int{0: 1}
    for _, num := range nums {
        sum += num
        if c, ok := prefixCount[sum-k]; ok {
            count += c
        }
        prefixCount[sum]++
    }
    return count
}

// Product of array except self (LC 238)
func productExceptSelf(nums []int) []int {
    n := len(nums)
    result := make([]int, n)
    // prefix products from left
    result[0] = 1
    for i := 1; i < n; i++ {
        result[i] = result[i-1] * nums[i-1]
    }
    // multiply by suffix products from right
    right := 1
    for i := n - 1; i >= 0; i-- {
        result[i] *= right
        right *= nums[i]
    }
    return result
}
```

## Union-Find / Disjoint Set

### Overview
```
union_find:
  what: Data structure to track elements partitioned into disjoint sets
  operations:
    find: Determine which set an element belongs to (with path compression)
    union: Merge two sets (with union by rank)

  when_to_recognize:
    - "Connected components"
    - "Are two elements in the same group?"
    - "Merge groups"
    - Kruskal's MST
    - Dynamic connectivity

  time_complexity: O(alpha(n)) per operation, nearly O(1) amortized
  space_complexity: O(n)
```

### Implementation
```go
type UnionFind struct {
    parent []int
    rank   []int
    count  int // number of connected components
}

func NewUnionFind(n int) *UnionFind {
    parent := make([]int, n)
    rank := make([]int, n)
    for i := range parent {
        parent[i] = i
    }
    return &UnionFind{parent: parent, rank: rank, count: n}
}

func (uf *UnionFind) Find(x int) int {
    if uf.parent[x] != x {
        uf.parent[x] = uf.Find(uf.parent[x]) // path compression
    }
    return uf.parent[x]
}

func (uf *UnionFind) Union(x, y int) bool {
    px, py := uf.Find(x), uf.Find(y)
    if px == py {
        return false // already connected
    }
    // union by rank
    if uf.rank[px] < uf.rank[py] {
        px, py = py, px
    }
    uf.parent[py] = px
    if uf.rank[px] == uf.rank[py] {
        uf.rank[px]++
    }
    uf.count--
    return true
}

func (uf *UnionFind) Connected(x, y int) bool {
    return uf.Find(x) == uf.Find(y)
}

// Number of connected components using Union-Find
func countComponents(n int, edges [][]int) int {
    uf := NewUnionFind(n)
    for _, e := range edges {
        uf.Union(e[0], e[1])
    }
    return uf.count
}
```

## Topological Sort

### Overview
```
topological_sort:
  what: Linear ordering of vertices in a DAG where for every edge u->v, u comes before v
  approaches:
    kahns_bfs: Use in-degree tracking and BFS (easier to implement)
    dfs_based: Post-order DFS with reversal

  when_to_recognize:
    - "Order of tasks with dependencies"
    - "Course schedule" problems
    - Build system dependency resolution
    - "Is it possible to finish all tasks?"

  time_complexity: O(V + E)
  space_complexity: O(V + E)
```

### Implementation
```go
// Kahn's algorithm (BFS) - also detects cycles
func topologicalSort(numNodes int, edges [][]int) ([]int, bool) {
    graph := make([][]int, numNodes)
    inDegree := make([]int, numNodes)
    for _, e := range edges {
        graph[e[0]] = append(graph[e[0]], e[1])
        inDegree[e[1]]++
    }
    queue := []int{}
    for i := 0; i < numNodes; i++ {
        if inDegree[i] == 0 {
            queue = append(queue, i)
        }
    }
    order := []int{}
    for len(queue) > 0 {
        node := queue[0]
        queue = queue[1:]
        order = append(order, node)
        for _, neighbor := range graph[node] {
            inDegree[neighbor]--
            if inDegree[neighbor] == 0 {
                queue = append(queue, neighbor)
            }
        }
    }
    if len(order) != numNodes {
        return nil, false // cycle detected
    }
    return order, true
}

// Course Schedule II (LC 210)
func findOrder(numCourses int, prerequisites [][]int) []int {
    graph := make([][]int, numCourses)
    inDegree := make([]int, numCourses)
    for _, p := range prerequisites {
        graph[p[1]] = append(graph[p[1]], p[0])
        inDegree[p[0]]++
    }
    queue := []int{}
    for i := 0; i < numCourses; i++ {
        if inDegree[i] == 0 {
            queue = append(queue, i)
        }
    }
    order := []int{}
    for len(queue) > 0 {
        course := queue[0]
        queue = queue[1:]
        order = append(order, course)
        for _, next := range graph[course] {
            inDegree[next]--
            if inDegree[next] == 0 {
                queue = append(queue, next)
            }
        }
    }
    if len(order) != numCourses {
        return nil
    }
    return order
}
```

## Trie

### Overview
```
trie:
  what: Tree-like data structure for efficient string prefix operations
  also_called: Prefix tree

  when_to_recognize:
    - "Prefix matching / autocomplete"
    - "Word search in dictionary"
    - "Count words with given prefix"
    - String-based search optimization

  time_complexity: O(L) per operation where L is word length
  space_complexity: O(N * L) where N is number of words
```

### Implementation
```go
type TrieNode struct {
    children [26]*TrieNode
    isEnd    bool
}

type Trie struct {
    root *TrieNode
}

func NewTrie() *Trie {
    return &Trie{root: &TrieNode{}}
}

func (t *Trie) Insert(word string) {
    node := t.root
    for _, ch := range word {
        idx := ch - 'a'
        if node.children[idx] == nil {
            node.children[idx] = &TrieNode{}
        }
        node = node.children[idx]
    }
    node.isEnd = true
}

func (t *Trie) Search(word string) bool {
    node := t.root
    for _, ch := range word {
        idx := ch - 'a'
        if node.children[idx] == nil {
            return false
        }
        node = node.children[idx]
    }
    return node.isEnd
}

func (t *Trie) StartsWith(prefix string) bool {
    node := t.root
    for _, ch := range prefix {
        idx := ch - 'a'
        if node.children[idx] == nil {
            return false
        }
        node = node.children[idx]
    }
    return true
}

// Word Search II (LC 212) - find all words in board using Trie
func findWords(board [][]byte, words []string) []string {
    trie := NewTrie()
    for _, w := range words {
        trie.Insert(w)
    }
    rows, cols := len(board), len(board[0])
    result := map[string]bool{}
    var dfs func(r, c int, node *TrieNode, path string)
    dfs = func(r, c int, node *TrieNode, path string) {
        if r < 0 || r >= rows || c < 0 || c >= cols || board[r][c] == '#' {
            return
        }
        ch := board[r][c]
        next := node.children[ch-'a']
        if next == nil {
            return
        }
        path += string(ch)
        if next.isEnd {
            result[path] = true
        }
        board[r][c] = '#'
        dfs(r+1, c, next, path)
        dfs(r-1, c, next, path)
        dfs(r, c+1, next, path)
        dfs(r, c-1, next, path)
        board[r][c] = ch
    }
    for r := 0; r < rows; r++ {
        for c := 0; c < cols; c++ {
            dfs(r, c, trie.root, "")
        }
    }
    out := []string{}
    for w := range result {
        out = append(out, w)
    }
    return out
}
```

## Quick Reference
```
pattern_selection_guide:
  sorted_array_pair_target: Two Pointers (opposite direction)
  remove_duplicates_in_place: Two Pointers (same direction)
  contiguous_subarray_max_sum: Sliding Window or Kadane's
  subarray_of_size_k: Fixed Sliding Window
  longest_substring_condition: Variable Sliding Window
  find_element_in_sorted: Binary Search
  minimize_maximum_value: Binary Search on Answer Space
  shortest_path_unweighted: BFS
  find_all_paths: DFS / Backtracking
  all_combinations_permutations: Backtracking
  min_max_cost_with_choices: Dynamic Programming
  count_number_of_ways: Dynamic Programming
  interval_problems: Greedy (sort by start or end)
  next_greater_element: Monotonic Stack
  range_sum_queries: Prefix Sum
  connected_components: Union-Find or DFS
  task_ordering_dependencies: Topological Sort
  prefix_matching_autocomplete: Trie
```
