# React Query (TanStack Query)

TanStack Query (formerly React Query) is a **server-state management library** for React. It handles fetching, caching, synchronizing, and updating server state — eliminating the need for global state managers (Redux, Zustand) for async data.

---

## Why React Query?

| Problem | Without React Query | With React Query |
|---|---|---|
| Loading/error states | Manual `useState` + `useEffect` | Built-in `isLoading`, `isError` |
| Caching | None or manual | Automatic with configurable stale time |
| Refetching | Manual triggers | Auto refetch on window focus, interval, reconnect |
| Deduplication | Multiple identical requests | Single request, shared across components |
| Optimistic updates | Complex manual logic | Built-in support |
| Pagination/Infinite scroll | DIY | `useInfiniteQuery` |

---

## Installation

```bash
npm install @tanstack/react-query
# Optional devtools
npm install @tanstack/react-query-devtools
```

---

## Setup — QueryClientProvider

Wrap your app with `QueryClientProvider`. This provides the cache and configuration to all child components.

```jsx
// main.jsx or App.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // 5 minutes — data is "fresh" for this long
      gcTime: 1000 * 60 * 30,    // 30 minutes — unused cache lives this long
      retry: 2,                   // retry failed requests 2 times
      refetchOnWindowFocus: true, // refetch when user returns to tab
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

**Key concepts:**
- `staleTime` — how long fetched data is considered fresh (won't refetch)
- `gcTime` (formerly `cacheTime`) — how long inactive/unused cache is kept in memory
- Fresh data → served from cache instantly. Stale data → served from cache + background refetch.

---

## 1. Basic Query — `useQuery`

`useQuery` fetches and caches data. It requires a **query key** (unique identifier) and a **query function** (returns a promise).

```jsx
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const {
    data,         // the resolved data
    isLoading,    // true on first load (no cached data)
    isFetching,   // true whenever a request is in flight (including background refetches)
    isError,      // true if query failed
    error,        // the error object
    isSuccess,    // true if data is available
    refetch,      // function to manually trigger refetch
  } = useQuery({
    queryKey: ['user', userId],     // cache key — changes when userId changes
    queryFn: async () => {
      const res = await fetch(`/api/users/${userId}`);
      if (!res.ok) throw new Error('Failed to fetch user');
      return res.json();
    },
    enabled: !!userId,  // don't run query if userId is falsy (dependent query)
  });

  if (isLoading) return <p>Loading...</p>;
  if (isError) return <p>Error: {error.message}</p>;

  return (
    <div>
      <h1>{data.name}</h1>
      <p>{data.email}</p>
    </div>
  );
}
```

### Query Keys — The Cache Identity

Query keys are the **most important concept**. They determine cache identity and automatic refetching.

```jsx
// Simple key
useQuery({ queryKey: ['todos'], queryFn: fetchTodos });

// Key with variable — cache is separate per userId
useQuery({ queryKey: ['user', userId], queryFn: () => fetchUser(userId) });

// Key with filters — different cache entry for each filter combination
useQuery({
  queryKey: ['todos', { status: 'done', page: 3 }],
  queryFn: () => fetchTodos({ status: 'done', page: 3 }),
});
```

> When any part of the query key changes, React Query automatically refetches.

---

## 2. Mutations — `useMutation`

Mutations are for **creating, updating, or deleting** data. Unlike queries, mutations don't run automatically — you call `mutate()` explicitly.

```jsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreateTodo() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');

  const mutation = useMutation({
    mutationFn: async (newTodo) => {
      const res = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTodo),
      });
      if (!res.ok) throw new Error('Failed to create todo');
      return res.json();
    },
    onSuccess: (data) => {
      // Invalidate the todos cache so it refetches with the new item
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      setTitle('');
    },
    onError: (error) => {
      alert(`Error: ${error.message}`);
    },
  });

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      mutation.mutate({ title });
    }}>
      <input value={title} onChange={(e) => setTitle(e.target.value)} />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Adding...' : 'Add Todo'}
      </button>
      {mutation.isError && <p>Error: {mutation.error.message}</p>}
    </form>
  );
}
```

### Mutation Lifecycle Callbacks

```jsx
useMutation({
  mutationFn: updateTodo,
  onMutate: (variables) => {
    // Fires before mutation — great for optimistic updates
    console.log('About to update:', variables);
  },
  onSuccess: (data, variables, context) => {
    // Fires on success
  },
  onError: (error, variables, context) => {
    // Fires on error
  },
  onSettled: (data, error, variables, context) => {
    // Fires on both success and error (like finally)
  },
});
```

---

## 3. Optimistic Updates

Update the UI **before** the server responds, then roll back if it fails.

```jsx
function useUpdateTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (updatedTodo) =>
      fetch(`/api/todos/${updatedTodo.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTodo),
      }).then(res => res.json()),

    onMutate: async (updatedTodo) => {
      // 1. Cancel outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ queryKey: ['todos'] });

      // 2. Snapshot the previous value (for rollback)
      const previousTodos = queryClient.getQueryData(['todos']);

      // 3. Optimistically update the cache
      queryClient.setQueryData(['todos'], (old) =>
        old.map(todo =>
          todo.id === updatedTodo.id ? { ...todo, ...updatedTodo } : todo
        )
      );

      // 4. Return snapshot for rollback
      return { previousTodos };
    },

    onError: (err, updatedTodo, context) => {
      // Rollback to the snapshot
      queryClient.setQueryData(['todos'], context.previousTodos);
    },

    onSettled: () => {
      // Refetch to ensure server state is in sync
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

// Usage
function TodoItem({ todo }) {
  const updateTodo = useUpdateTodo();

  return (
    <label>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() =>
          updateTodo.mutate({ ...todo, completed: !todo.completed })
        }
      />
      {todo.title}
    </label>
  );
}
```

---

## 4. Pagination

```jsx
function PaginatedTodos() {
  const [page, setPage] = useState(1);

  const { data, isLoading, isPlaceholderData } = useQuery({
    queryKey: ['todos', { page }],
    queryFn: () => fetch(`/api/todos?page=${page}&limit=10`).then(r => r.json()),
    placeholderData: (previousData) => previousData,  // keep old data while fetching next page
  });

  return (
    <div>
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <>
          <ul style={{ opacity: isPlaceholderData ? 0.5 : 1 }}>
            {data.items.map(todo => (
              <li key={todo.id}>{todo.title}</li>
            ))}
          </ul>
          <button onClick={() => setPage(p => p - 1)} disabled={page === 1}>
            Prev
          </button>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={!data.hasMore}
          >
            Next
          </button>
        </>
      )}
    </div>
  );
}
```

---

## 5. Infinite Scroll — `useInfiniteQuery`

```jsx
import { useInfiniteQuery } from '@tanstack/react-query';
import { useInView } from 'react-intersection-observer';

function InfiniteFeed() {
  const { ref, inView } = useInView();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['posts'],
    queryFn: async ({ pageParam }) => {
      const res = await fetch(`/api/posts?cursor=${pageParam}&limit=20`);
      return res.json();
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
  });

  // Auto-fetch when sentinel comes into view
  useEffect(() => {
    if (inView && hasNextPage) fetchNextPage();
  }, [inView, hasNextPage, fetchNextPage]);

  if (isLoading) return <p>Loading...</p>;

  return (
    <div>
      {data.pages.map((page, i) => (
        <Fragment key={i}>
          {page.items.map(post => (
            <PostCard key={post.id} post={post} />
          ))}
        </Fragment>
      ))}
      <div ref={ref}>
        {isFetchingNextPage ? 'Loading more...' : hasNextPage ? '' : 'No more posts'}
      </div>
    </div>
  );
}
```

**How it works:**
- `data.pages` is an array of all fetched pages
- `getNextPageParam` extracts the cursor/offset for the next page from the last fetched page
- Returns `undefined` to signal no more pages (`hasNextPage` becomes false)

---

## 6. Dependent (Serial) Queries

Run a query only after another query has resolved.

```jsx
function UserPosts({ userId }) {
  // First: fetch user
  const userQuery = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  // Second: fetch posts — only runs when user data is available
  const postsQuery = useQuery({
    queryKey: ['posts', userQuery.data?.id],
    queryFn: () => fetchPostsByUser(userQuery.data.id),
    enabled: !!userQuery.data?.id,  // won't execute until user is loaded
  });

  if (userQuery.isLoading) return <p>Loading user...</p>;
  if (postsQuery.isLoading) return <p>Loading posts...</p>;

  return (
    <div>
      <h1>{userQuery.data.name}'s Posts</h1>
      {postsQuery.data.map(post => (
        <p key={post.id}>{post.title}</p>
      ))}
    </div>
  );
}
```

---

## 7. Parallel Queries

```jsx
import { useQueries } from '@tanstack/react-query';

function Dashboard({ userIds }) {
  const results = useQueries({
    queries: userIds.map(id => ({
      queryKey: ['user', id],
      queryFn: () => fetchUser(id),
    })),
  });

  const isLoading = results.some(r => r.isLoading);
  const allUsers = results.map(r => r.data).filter(Boolean);

  if (isLoading) return <p>Loading...</p>;

  return (
    <ul>
      {allUsers.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

---

## 8. Prefetching

Fetch data before the user needs it (e.g., on hover).

```jsx
function TodoList() {
  const queryClient = useQueryClient();

  const handleHover = (todoId) => {
    queryClient.prefetchQuery({
      queryKey: ['todo', todoId],
      queryFn: () => fetchTodo(todoId),
      staleTime: 1000 * 60 * 5,  // won't refetch if already fresh
    });
  };

  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id} onMouseEnter={() => handleHover(todo.id)}>
          <Link to={`/todo/${todo.id}`}>{todo.title}</Link>
        </li>
      ))}
    </ul>
  );
}
```

---

## 9. Query Invalidation & Cache Manipulation

```jsx
const queryClient = useQueryClient();

// Invalidate — marks as stale and refetches active queries
queryClient.invalidateQueries({ queryKey: ['todos'] });           // all todo queries
queryClient.invalidateQueries({ queryKey: ['todos', { page: 1 }] }); // specific
queryClient.invalidateQueries();                                    // everything

// Set cache directly (no network request)
queryClient.setQueryData(['user', userId], updatedUser);

// Read cache
const cachedUser = queryClient.getQueryData(['user', userId]);

// Remove from cache entirely
queryClient.removeQueries({ queryKey: ['user', userId] });

// Cancel ongoing queries
queryClient.cancelQueries({ queryKey: ['todos'] });
```

---

## 10. Polling (Auto Refetch on Interval)

```jsx
function LiveStockPrice({ symbol }) {
  const { data } = useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => fetchStockPrice(symbol),
    refetchInterval: 3000,                   // poll every 3 seconds
    refetchIntervalInBackground: true,       // keep polling even when tab is hidden
  });

  return <p>{symbol}: ${data?.price}</p>;
}
```

---

## 11. Custom Hook Pattern (Recommended)

Extract queries into reusable hooks — keeps components clean.

```jsx
// hooks/useTodos.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API = '/api/todos';

export function useTodos(filters) {
  return useQuery({
    queryKey: ['todos', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const res = await fetch(`${API}?${params}`);
      if (!res.ok) throw new Error('Failed to fetch todos');
      return res.json();
    },
  });
}

export function useCreateTodo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (newTodo) => {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTodo),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

export function useDeleteTodo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => fetch(`${API}/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

// Component usage — clean and focused
function TodoApp() {
  const { data: todos, isLoading } = useTodos({ status: 'active' });
  const createTodo = useCreateTodo();
  const deleteTodo = useDeleteTodo();

  // ...render
}
```

---

## 12. Error Handling with Error Boundaries

```jsx
import { QueryErrorResetBoundary } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ resetErrorBoundary, error }) => (
            <div>
              <p>Something went wrong: {error.message}</p>
              <button onClick={resetErrorBoundary}>Try again</button>
            </div>
          )}
        >
          <Todos />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}

// In the query — throwOnError pushes errors to the boundary
function Todos() {
  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    throwOnError: true,  // propagate to ErrorBoundary
  });

  return <ul>{data.map(t => <li key={t.id}>{t.title}</li>)}</ul>;
}
```

---

## 13. Using with Axios

```jsx
import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

// Axios throws on non-2xx by default — works perfectly with React Query
export function usePosts() {
  return useQuery({
    queryKey: ['posts'],
    queryFn: () => api.get('/posts').then(res => res.data),
  });
}

export function useCreatePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (newPost) => api.post('/posts', newPost).then(res => res.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['posts'] }),
  });
}
```

---

## Quick Reference — Mental Model

```
Component mounts
  → useQuery checks cache for queryKey
    → Cache HIT + fresh     → return cached data (no request)
    → Cache HIT + stale     → return cached data + background refetch
    → Cache MISS            → fetch + show isLoading
  → Data cached under queryKey
  → Component unmounts → cache kept for gcTime → then garbage collected

Mutation fires
  → mutationFn runs → onSuccess/onError/onSettled callbacks
  → You call invalidateQueries → stale queries refetch
```

---

## Common Options Cheatsheet

| Option | Default | Description |
|---|---|---|
| `staleTime` | `0` | How long data is fresh (ms) |
| `gcTime` | `5 min` | How long unused cache is kept |
| `retry` | `3` | Number of retries on failure |
| `retryDelay` | exponential | Delay between retries |
| `refetchOnWindowFocus` | `true` | Refetch when tab regains focus |
| `refetchOnMount` | `true` | Refetch when component mounts |
| `refetchOnReconnect` | `true` | Refetch when network reconnects |
| `refetchInterval` | `false` | Polling interval (ms) |
| `enabled` | `true` | Whether query runs automatically |
| `placeholderData` | — | Shown while loading (not cached) |
| `initialData` | — | Seed cache (treated as real data) |
| `select` | — | Transform/filter data before returning |
| `throwOnError` | `false` | Propagate errors to error boundaries |
