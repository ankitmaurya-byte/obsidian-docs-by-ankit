
# Java Collections Cheat Sheet

## Arrays
```yaml
type: Fixed size contiguous memory
package: java.lang
declaration: int[] arr = new int[n]

properties:
  - fixed_size
  - O(1)_random_access
  - no_dynamic_resize

operations:
  traverse: for (int i = 0; i < arr.length; i++)
  sort: Arrays.sort(arr)
  binary_search: Arrays.binarySearch(arr, key)

time_complexity:
  access: O(1)
  search: O(n)
  insert_delete: O(n)
````

---

## List Interface

### ArrayList

```yaml
type: Dynamic array
package: java.util
declaration: List<Integer> list = new ArrayList<>()

properties:
  - resizable_array
  - fast_random_access

time_complexity:
  get: O(1)
  add_end: O(1)
  add_middle: O(n)
  remove: O(n)
```

### LinkedList

```yaml
type: Doubly linked list
package: java.util
declaration: List<Integer> list = new LinkedList<>()

properties:
  - fast_insertion_deletion
  - sequential_access

time_complexity:
  get: O(n)
  add_remove_head_tail: O(1)
```

### Vector (Legacy)

```yaml
type: Synchronized dynamic array
note: rarely_used

time_complexity:
  similar_to_arraylist: true
```

### Stack

```yaml
type: LIFO
package: java.util
declaration: Stack<Integer> st = new Stack<>()

operations:
  push: O(1)
  pop: O(1)
  peek: O(1)
```

---

## Queue Interface

### LinkedList (Queue)

```yaml
declaration: Queue<Integer> q = new LinkedList<>()
```

### PriorityQueue (Heap)

```yaml
type: Min Heap
declaration: PriorityQueue<Integer> pq = new PriorityQueue<>()

properties:
  - heap_structure
  - sorted_removal

time_complexity:
  add: O(log n)
  remove: O(log n)
  peek: O(1)
```

### Deque

#### ArrayDeque

```yaml
type: Double ended queue
declaration: Deque<Integer> dq = new ArrayDeque<>()

properties:
  - faster_than_stack
  - no_synchronization
```

---

## Set Interface

### HashSet

```yaml
type: Hash table
declaration: Set<Integer> set = new HashSet<>()

properties:
  - unique_elements
  - unordered

time_complexity:
  add_remove_contains: O(1)
```

### LinkedHashSet

```yaml
type: Maintains insertion order

time_complexity:
  add_remove_contains: O(1)
```

### TreeSet

```yaml
type: Balanced BST
declaration: Set<Integer> set = new TreeSet<>()

properties:
  - sorted_order

time_complexity:
  add_remove_contains: O(log n)
```

---

## Map Interface

### HashMap

```yaml
type: Hash table
declaration: Map<Integer, String> map = new HashMap<>()

properties:
  - no_order
  - allows_one_null_key

time_complexity:
  put_get_remove: O(1)
```

### LinkedHashMap

```yaml
type: Maintains insertion order

time_complexity:
  put_get_remove: O(1)
```

### TreeMap

```yaml
type: Red Black Tree
declaration: Map<Integer, String> map = new TreeMap<>()

properties:
  - sorted_keys

time_complexity:
  put_get_remove: O(log n)
```

### Hashtable (Legacy)

```yaml
type: Synchronized HashMap
note: rarely_used
```

---

## Iterator

```yaml
usage:
  Iterator<Integer> it = list.iterator()

methods:
  hasNext: check_next_element
  next: get_next_element
  remove: delete_current_element
```

---

## Quick Interview Summary

```yaml
when_to_use:

  arraylist: fast_read_operations
  linkedlist: frequent_insert_delete
  hashmap: key_value_lookup
  hashset: uniqueness_check
  priorityqueue: top_k_elements
  treeset_treemap: sorted_data
  deque: sliding_window / stack_queue_combo
```





## ArrayList uses dynamic array, HashMap uses hashing with buckets and tree optimization, TreeMap uses Red-Black tree, and PriorityQueue uses binary heap — each chosen based on access vs ordering vs mutation trade-offs
# Java Collections – Use Cases + CRUD (Obsidian)

---
## ArrayList
```yaml
use_case:
  - fast_random_access
  - read_heavy_operations

declaration: List<Integer> list = new ArrayList<>()

crud:
  create:
    - list.add(10)
    - list.add(index, value)
  read:
    - list.get(index)
  update:
    - list.set(index, value)
  delete:
    - list.remove(index)
    - list.remove(Integer.valueOf(val))

important_functions:
  - list.contains(val)
  - list.size()
  - Collections.sort(list)
````

---

## LinkedList

```yaml
use_case:
  - frequent_insert_delete
  - queue_or_deque_usage

declaration: List<Integer> list = new LinkedList<>()

crud:
  create:
    - list.add(val)
    - list.addFirst(val)
    - list.addLast(val)
  read:
    - list.get(index)
    - list.peek()
  update:
    - list.set(index, val)
  delete:
    - list.remove(index)
    - list.removeFirst()
    - list.removeLast()

important_functions:
  - list.peek()
  - list.poll()
```

---

## HashSet

```yaml
use_case:
  - uniqueness_check
  - duplicate_removal

declaration: Set<Integer> set = new HashSet<>()

crud:
  create:
    - set.add(val)
  read:
    - set.contains(val)
  update: not_supported
  delete:
    - set.remove(val)

important_functions:
  - set.size()
  - set.isEmpty()
```

---

## TreeSet

```yaml
use_case:
  - sorted_unique_data
  - range_queries

declaration: Set<Integer> set = new TreeSet<>()

crud:
  create:
    - set.add(val)
  read:
    - set.contains(val)declaration: Set<Integer> set = new TreeSet<>()

  update: not_supported
  delete:
    - set.remove(val)

important_functions:
  - set.first()
  - set.last()
  - set.floor(val)
  - set.ceiling(val)
```

---

## HashMap

```yaml
use_case:
  - fast_key_value_lookup
  - frequency_count

declaration: Map<Integer, String> map = new HashMap<>()

crud:
  create:
    - map.put(key, value)
  read:
    - map.get(key)
  update:
    - map.put(key, newValue)
  delete:
    - map.remove(key)

important_functions:
  - map.containsKey(key)
  - map.containsValue(val)
  - map.size()

iteration:
  - for (Map.Entry<K,V> e : map.entrySet())
```

---

## TreeMap

```yaml
use_case:
  - sorted_keys
  - range_queries

declaration: Map<Integer, String> map = new TreeMap<>()

crud:
  create:
    - map.put(key, value)
  read:
    - map.get(key)
  update:
    - map.put(key, newValue)
  delete:
    - map.remove(key)

important_functions:
  - map.firstKey()
  - map.lastKey()
  - map.floorKey(key)
  - map.ceilingKey(key)
```

---

## PriorityQueue

```yaml
use_case:
  - top_k_elements
  - heap_operations

declaration: Queue<Integer> pq = new PriorityQueue<>()

crud:
  create:
    - pq.add(val)
  read:
    - pq.peek()
  update: not_direct
  delete:
    - pq.poll()

important_functions:
  - pq.size()

notes:
  - default_min_heap
  - max_heap: new PriorityQueue<>(Collections.reverseOrder())
```

---

## Deque (ArrayDeque)

```yaml
use_case:
  - sliding_window
  - stack_and_queue

declaration: Deque<Integer> dq = new ArrayDeque<>()

crud:
  create:
    - dq.addFirst(val)
    - dq.addLast(val)
  read:
    - dq.peekFirst()
    - dq.peekLast()
  update: not_direct
  delete:
    - dq.removeFirst()
    - dq.removeLast()

important_functions:
  - dq.push(val)
  - dq.pop()
  - dq.offer(val)
  - dq.poll()
```

---

## Quick Mapping

```yaml
arraylist: indexing_read_heavy
linkedlist: frequent_insert_delete
hashset: uniqueness_check
treeset: sorted_unique
hashmap: fast_lookup
treemap: sorted_keys
priorityqueue: top_k
deque: sliding_window
```



# Java Collections – Internal + Complexity

---

## ArrayList
```yaml
structure: dynamic_array

time_complexity:
  access: O(1)
  add_end: O(1)_amortized
  add_middle: O(n)
  remove: O(n)
  search: O(n)

space_complexity:
  space: O(n)
  extra: resizing_array

internal_working:
  - backed_by_contiguous_array
  - resizing_creates_new_array
  - elements_shift_on_insert_delete
````

---

## LinkedList

```yaml
structure: doubly_linked_list

time_complexity:
  access: O(n)
  insert_delete_head_tail: O(1)
  insert_middle: O(n)
  search: O(n)

space_complexity:
  space: O(n)
  extra:
    - prev_pointer
    - next_pointer

internal_working:
  - each_node_has_prev_next
  - non_contiguous_memory
  - no_shifting_required
```

---

## HashSet

```yaml
structure: hash_table

time_complexity:
  add: O(1)
  remove: O(1)
  contains: O(1)
  worst_case: O(n)

space_complexity:
  space: O(n)
  extra: buckets

internal_working:
  - uses_hashmap_internally
  - elements_stored_as_keys
  - collision_handling:
      - linked_list
      - tree_after_threshold_java8
```

---

## TreeSet

```yaml
structure: red_black_tree

time_complexity:
  add: O(log n)
  remove: O(log n)
  contains: O(log n)

space_complexity:
  space: O(n)

internal_working:
  - self_balancing_bst
  - maintains_sorted_order
```

---

## HashMap

```yaml
structure: hash_table

time_complexity:
  put: O(1)
  get: O(1)
  remove: O(1)
  worst_case: O(n)

space_complexity:
  space: O(n)
  extra:
    - bucket_array
    - node_objects

internal_working:
  - array_of_buckets
  - hash_function_generates_index
  - collision_handling:
      - linked_list
      - tree_java8+
  - load_factor: 0.75
  - resizing_doubles_capacity
```

---

## TreeMap

```yaml
structure: red_black_tree

time_complexity:
  put: O(log n)
  get: O(log n)
  remove: O(log n)

space_complexity:
  space: O(n)

internal_working:
  - self_balancing_tree
  - maintains_key_order
```

---

## PriorityQueue

```yaml
structure: binary_heap_array

time_complexity:
  add: O(log n)
  poll: O(log n)
  peek: O(1)

space_complexity:
  space: O(n)

internal_working:
  - complete_binary_tree
  - stored_in_array
  - heap_property_maintained
```

---

## Deque (ArrayDeque)

```yaml
structure: circular_array

time_complexity:
  add_first_last: O(1)
  remove_first_last: O(1)
  peek: O(1)

space_complexity:
  space: O(n)

internal_working:
  - circular_buffer
  - head_tail_pointers
  - no_shifting
```

---

## Quick Summary

```yaml
arraylist: dynamic_array_fast_access
linkedlist: pointer_based_insert_delete
hashset: hash_table_uniqueness
treeset: red_black_tree_sorted
hashmap: hash_table_fast_lookup
treemap: red_black_tree_sorted_map
priorityqueue: binary_heap_top_k
deque: circular_array_sliding_window
```

```
```
