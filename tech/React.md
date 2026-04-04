# React

## What is React
```
overview:
  what: A JavaScript library for building user interfaces
  created_by: Meta (Facebook), 2013
  key_concepts:
    - Component-based architecture
    - Declarative UI (describe what, not how)
    - Virtual DOM for efficient updates
    - Unidirectional data flow (parent -> child via props)
    - JSX syntax (HTML-like in JavaScript)
  ecosystem:
    routing: React Router
    state_management: Context API, Redux, Zustand, Jotai
    meta_frameworks: Next.js, Remix
    styling: CSS Modules, Tailwind, styled-components
```

## JSX
```
jsx:
  what: JavaScript XML - syntax extension that lets you write HTML-like code in JS
  how_it_works:
    - JSX is transformed to React.createElement() calls by the compiler (Babel/SWC)
    - Returns React elements (plain objects describing UI)
  rules:
    - Must return a single root element (use fragments <></> to avoid extra DOM nodes)
    - Use className instead of class
    - Use htmlFor instead of for
    - Self-close tags with no children (<img />, <br />)
    - JavaScript expressions inside curly braces {}
    - camelCase for HTML attributes (onClick, tabIndex, onChange)
```

```jsx
// JSX basics
function Greeting({ name }) {
  const isLoggedIn = true;

  return (
    <>
      <h1>Hello, {name}!</h1>

      {/* Conditional rendering */}
      {isLoggedIn ? <p>Welcome back</p> : <p>Please log in</p>}

      {/* Short-circuit for show/hide */}
      {isLoggedIn && <button>Dashboard</button>}

      {/* Rendering lists - always provide key */}
      <ul>
        {["React", "Vue", "Svelte"].map((fw) => (
          <li key={fw}>{fw}</li>
        ))}
      </ul>

      {/* Inline styles (object with camelCase) */}
      <p style={{ color: "red", fontSize: "14px" }}>Styled text</p>
    </>
  );
}
```

## Components (Functional)
```
components:
  what: Reusable, independent pieces of UI that accept props and return JSX
  functional_components:
    - Plain JavaScript functions that return JSX
    - Use hooks for state and lifecycle
    - Preferred over class components in modern React
  best_practices:
    - Single responsibility (one component, one purpose)
    - Keep components small and focused
    - Extract logic into custom hooks
    - Use composition over inheritance
    - Co-locate related files (component + styles + tests)
```

```jsx
// Basic component with props
function UserCard({ name, role, avatar, onEdit }) {
  return (
    <div className="user-card">
      <img src={avatar} alt={name} />
      <h3>{name}</h3>
      <span>{role}</span>
      <button onClick={onEdit}>Edit</button>
    </div>
  );
}

// Component with children
function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-body">{children}</div>
    </div>
  );
}

// Usage
function App() {
  return (
    <Card title="Welcome">
      <p>This is the card content</p>
      <UserCard name="Ankit" role="Developer" avatar="/img.png" onEdit={() => {}} />
    </Card>
  );
}

// Default props
function Button({ variant = "primary", size = "md", children, ...rest }) {
  return (
    <button className={`btn btn-${variant} btn-${size}`} {...rest}>
      {children}
    </button>
  );
}
```

## Hooks

### useState
```
useState:
  what: "Hook to add state to functional components"
  syntax: "const [state, setState] = useState(initialValue)"
  key_points:
    - setState triggers a re-render
    - State updates are batched (multiple setState calls in one render cycle)
    - Use functional update when new state depends on previous state
    - State is preserved between re-renders
    - Initial value is only used on first render
```

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      {/* Functional update - safe when depending on previous state */}
      <button onClick={() => setCount((prev) => prev + 1)}>+1</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}

// Object state
function Form() {
  const [form, setForm] = useState({ name: "", email: "" });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value })); // spread to preserve other fields
  };

  return (
    <form>
      <input name="name" value={form.name} onChange={handleChange} />
      <input name="email" value={form.email} onChange={handleChange} />
    </form>
  );
}

// Lazy initialization (expensive initial value)
const [data, setData] = useState(() => {
  return JSON.parse(localStorage.getItem("data")) || [];
});
```

### useEffect
```
useEffect:
  what: "Hook to perform side effects (data fetching, subscriptions, DOM manipulation)"
  syntax: "useEffect(callback, dependencies)"
  dependency_array:
    no_array: "Runs after every render"
    empty_array: "Runs once on mount, cleanup on unmount"
    with_deps: "Runs when any dependency changes"
  cleanup:
    what: "Return a function from the effect to clean up (unsubscribe, cancel timers)"
    when: "Runs before the effect re-runs and on unmount"
  rules:
    - Don't lie about dependencies (include all referenced variables)
    - Use multiple useEffect calls for unrelated side effects
```

```jsx
import { useState, useEffect } from "react";

// Fetch data on mount
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false; // prevent state update after unmount

    async function fetchUser() {
      setLoading(true);
      try {
        const res = await fetch(`/api/users/${userId}`);
        const data = await res.json();
        if (!cancelled) {
          setUser(data);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) setLoading(false);
      }
    }

    fetchUser();

    return () => {
      cancelled = true; // cleanup: cancel if userId changes or unmount
    };
  }, [userId]); // re-run when userId changes

  if (loading) return <p>Loading...</p>;
  return <h1>{user?.name}</h1>;
}

// Event listener with cleanup
function WindowSize() {
  const [size, setSize] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setSize(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize); // cleanup
  }, []); // empty = mount/unmount only

  return <p>Width: {size}px</p>;
}

// Document title sync
useEffect(() => {
  document.title = `You have ${count} items`;
}, [count]);
```

### useContext
```
useContext:
  what: "Hook to consume values from a React Context without prop drilling"
  pattern:
    1: "Create context with createContext(defaultValue)"
    2: "Wrap provider around component tree with a value"
    3: "Consume with useContext(MyContext) in any child"
  when_to_use:
    - Theme (dark/light mode)
    - Authentication state
    - Locale/language
    - Any global-ish state shared across many components
  performance_note: "All consumers re-render when context value changes - split contexts if needed"
```

```jsx
import { createContext, useContext, useState } from "react";

// 1. Create context
const ThemeContext = createContext("light");

// 2. Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. Consume in any child
function ThemedButton() {
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <button
      onClick={toggleTheme}
      style={{
        background: theme === "dark" ? "#333" : "#fff",
        color: theme === "dark" ? "#fff" : "#333",
      }}
    >
      Current: {theme}
    </button>
  );
}

// Usage
function App() {
  return (
    <ThemeProvider>
      <ThemedButton />
    </ThemeProvider>
  );
}
```

### useReducer
```
useReducer:
  what: "Hook for complex state logic, alternative to useState"
  syntax: "const [state, dispatch] = useReducer(reducer, initialState)"
  when_to_use:
    - Multiple related state values
    - Complex state transitions
    - Next state depends on previous state
    - State logic you want to test independently
  pattern: "Similar to Redux - dispatch actions, reducer returns new state"
```

```jsx
import { useReducer } from "react";

const initialState = { count: 0, step: 1 };

function reducer(state, action) {
  switch (action.type) {
    case "increment":
      return { ...state, count: state.count + state.step };
    case "decrement":
      return { ...state, count: state.count - state.step };
    case "setStep":
      return { ...state, step: action.payload };
    case "reset":
      return initialState;
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div>
      <p>Count: {state.count} (step: {state.step})</p>
      <button onClick={() => dispatch({ type: "increment" })}>+</button>
      <button onClick={() => dispatch({ type: "decrement" })}>-</button>
      <input
        type="number"
        value={state.step}
        onChange={(e) =>
          dispatch({ type: "setStep", payload: Number(e.target.value) })
        }
      />
      <button onClick={() => dispatch({ type: "reset" })}>Reset</button>
    </div>
  );
}
```

### useMemo and useCallback
```
memoization_hooks:
  useMemo:
    what: "Memoize an expensive computed value - recalculates only when dependencies change"
    syntax: "const value = useMemo(() => expensiveCalc(a, b), [a, b])"
    returns: "The memoized value"

  useCallback:
    what: "Memoize a function reference - returns same function unless dependencies change"
    syntax: "const fn = useCallback((args) => { ... }, [deps])"
    returns: "The memoized function"
    main_use: "Prevent unnecessary re-renders of child components that receive the function as prop"

  when_to_use:
    - Expensive calculations (useMemo)
    - Passing callbacks to optimized child components (useCallback)
    - Referential equality matters (dependency of another hook)
  when_NOT_to_use:
    - Simple calculations (overhead of memoization > cost of recalculating)
    - Premature optimization
```

```jsx
import { useMemo, useCallback, useState, memo } from "react";

function ProductList({ products, onAddToCart }) {
  // useMemo - expensive filtering/sorting
  const [filter, setFilter] = useState("");

  const filteredProducts = useMemo(() => {
    console.log("Filtering...");
    return products.filter((p) =>
      p.name.toLowerCase().includes(filter.toLowerCase())
    );
  }, [products, filter]); // only recalculates when products or filter changes

  // useCallback - stable function reference for child
  const handleAddToCart = useCallback(
    (productId) => {
      onAddToCart(productId);
    },
    [onAddToCart]
  );

  return (
    <div>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} />
      {filteredProducts.map((p) => (
        <ProductItem key={p.id} product={p} onAdd={handleAddToCart} />
      ))}
    </div>
  );
}

// memo - skip re-render if props haven't changed
const ProductItem = memo(function ProductItem({ product, onAdd }) {
  console.log(`Rendering ${product.name}`);
  return (
    <div>
      <span>{product.name}</span>
      <button onClick={() => onAdd(product.id)}>Add</button>
    </div>
  );
});
```

### useRef
```
useRef:
  what: "Hook that returns a mutable ref object persisted across renders"
  syntax: "const ref = useRef(initialValue)"
  key_points:
    - ref.current holds the value
    - Changing ref.current does NOT trigger a re-render
    - Persists across renders (unlike regular variables)
  use_cases:
    - Access DOM elements directly
    - Store mutable values that don't need re-render (timers, previous values)
    - Hold references to intervals/timeouts for cleanup
```

```jsx
import { useRef, useState, useEffect } from "react";

// DOM access
function TextInput() {
  const inputRef = useRef(null);

  const focusInput = () => {
    inputRef.current.focus();
  };

  return (
    <div>
      <input ref={inputRef} placeholder="Type here..." />
      <button onClick={focusInput}>Focus Input</button>
    </div>
  );
}

// Store previous value
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

function Counter() {
  const [count, setCount] = useState(0);
  const prevCount = usePrevious(count);

  return (
    <p>
      Now: {count}, Before: {prevCount}
    </p>
  );
}

// Timer reference
function Stopwatch() {
  const [time, setTime] = useState(0);
  const intervalRef = useRef(null);

  const start = () => {
    intervalRef.current = setInterval(() => {
      setTime((t) => t + 1);
    }, 1000);
  };

  const stop = () => {
    clearInterval(intervalRef.current);
  };

  useEffect(() => {
    return () => clearInterval(intervalRef.current); // cleanup on unmount
  }, []);

  return (
    <div>
      <p>{time}s</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
    </div>
  );
}
```

## Props and State Management
```
props_and_state:
  props:
    what: "Data passed from parent to child (read-only in child)"
    direction: "Top-down (unidirectional)"
    immutable: "Child cannot modify props directly"

  state:
    what: "Data owned and managed by the component itself"
    mutable: "Changed via setState/dispatch, triggers re-render"

  lifting_state_up:
    what: "Move shared state to closest common ancestor"
    when: "Two sibling components need to share/sync state"

  state_management_options:
    local_state: "useState/useReducer for component-specific state"
    context: "React Context for low-frequency global state (theme, auth)"
    external_libraries:
      Redux: "Predictable state container, complex apps, middleware"
      Zustand: "Lightweight, minimal boilerplate, hooks-based"
      Jotai: "Atomic state management, fine-grained updates"
      TanStack_Query: "Server state (fetching, caching, syncing)"
```

## Virtual DOM and Reconciliation
```
virtual_dom:
  what: "Lightweight JavaScript representation of the actual DOM tree"
  how_it_works:
    1: "State/props change triggers re-render"
    2: "React creates new virtual DOM tree"
    3: "Diffing algorithm compares new tree with previous tree"
    4: "React calculates minimum set of changes needed"
    5: "Batch applies only those changes to the real DOM"

  reconciliation_rules:
    - Different element types: destroy old tree, build new tree
    - Same element type: update only changed attributes
    - Lists: uses key prop to match elements efficiently
    - Same component type: update props, keep instance and state

  keys:
    purpose: "Help React identify which items changed, were added, or removed"
    rules:
      - Must be unique among siblings
      - Must be stable (don't use index for dynamic lists)
      - Use unique IDs from your data
    bad_key: "index (causes bugs when items are reordered/deleted)"
```

## React Router
```
react_router:
  what: "Standard routing library for React SPAs"
  version: "v6+ (current)"
  key_components:
    BrowserRouter: "Wraps app, uses HTML5 history API"
    Routes: "Container for Route definitions"
    Route: "Maps a URL path to a component"
    Link: "Declarative navigation (renders <a> tag)"
    NavLink: "Link with active state styling"
    Navigate: "Redirect component"
    Outlet: "Renders child route component (nested routes)"
  hooks:
    useNavigate: "Programmatic navigation"
    useParams: "Access URL parameters"
    useSearchParams: "Access/modify query string"
    useLocation: "Current location object"
```

```jsx
import {
  BrowserRouter, Routes, Route, Link, NavLink,
  useParams, useNavigate, Outlet, Navigate
} from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <nav>
        <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>
          Home
        </NavLink>
        <Link to="/users">Users</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/users" element={<UsersLayout />}>
          <Route index element={<UsersList />} />
          <Route path=":userId" element={<UserDetail />} />
        </Route>
        <Route path="/login" element={<Login />} />
        {/* Protected route */}
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route path="*" element={<h1>404 Not Found</h1>} />
      </Routes>
    </BrowserRouter>
  );
}

// Nested layout with Outlet
function UsersLayout() {
  return (
    <div>
      <h1>Users</h1>
      <Outlet /> {/* Renders child route */}
    </div>
  );
}

// URL params
function UserDetail() {
  const { userId } = useParams();
  return <h2>User ID: {userId}</h2>;
}

// Programmatic navigation
function Login() {
  const navigate = useNavigate();

  const handleLogin = async () => {
    await loginAPI();
    navigate("/dashboard", { replace: true });
  };

  return <button onClick={handleLogin}>Log in</button>;
}

// Auth guard
function RequireAuth({ children }) {
  const isAuthenticated = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}
```

## Custom Hooks
```
custom_hooks:
  what: "Reusable functions that encapsulate stateful logic using built-in hooks"
  naming: "Must start with 'use' prefix (useXxx)"
  rules:
    - Can call other hooks
    - Follow all hook rules (top-level only, not in conditions/loops)
    - Extract and share logic between components
    - Each usage gets its own independent state
```

```jsx
// useLocalStorage - persist state in localStorage
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// Usage
const [theme, setTheme] = useLocalStorage("theme", "light");

// useFetch - data fetching hook
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!cancelled) {
          setData(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [url]);

  return { data, loading, error };
}

// Usage
function UserList() {
  const { data: users, loading, error } = useFetch("/api/users");

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  return <ul>{users.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}

// useDebounce
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
```

## Performance Optimization
```
performance:
  avoid_unnecessary_renders:
    React.memo: "Wrap component to skip re-render if props unchanged"
    useMemo: "Memoize expensive computed values"
    useCallback: "Memoize function references passed as props"
    key_prop: "Use stable unique keys for lists"

  code_splitting:
    React.lazy: "Lazy load components (dynamic import)"
    Suspense: "Show fallback while lazy component loads"

  other_techniques:
    - Virtualize long lists (react-window, react-virtuoso)
    - Debounce rapid state updates (search inputs)
    - Avoid inline object/array creation in JSX
    - Use React DevTools Profiler to find bottlenecks
    - Split context to avoid unnecessary consumer re-renders
```

```jsx
import { lazy, Suspense, memo, useMemo, useCallback } from "react";

// Code splitting with lazy loading
const HeavyComponent = lazy(() => import("./HeavyComponent"));

function App() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <HeavyComponent />
    </Suspense>
  );
}

// Virtualized list (concept)
// Instead of rendering 10,000 items, only render visible ones
// Libraries: react-window, react-virtuoso
import { FixedSizeList } from "react-window";

function VirtualList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  );

  return (
    <FixedSizeList
      height={400}
      itemCount={items.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

## Todo App Example
```
todo_app:
  what: "Complete mini todo app demonstrating useState, useReducer, components, and hooks"
  features:
    - Add todo
    - Toggle complete
    - Delete todo
    - Filter (all, active, completed)
```

```jsx
import { useState, useReducer, useMemo } from "react";

// Reducer for todo state
function todosReducer(todos, action) {
  switch (action.type) {
    case "add":
      return [...todos, { id: Date.now(), text: action.text, completed: false }];
    case "toggle":
      return todos.map((t) =>
        t.id === action.id ? { ...t, completed: !t.completed } : t
      );
    case "delete":
      return todos.filter((t) => t.id !== action.id);
    default:
      return todos;
  }
}

function TodoApp() {
  const [todos, dispatch] = useReducer(todosReducer, []);
  const [input, setInput] = useState("");
  const [filter, setFilter] = useState("all"); // all | active | completed

  const filteredTodos = useMemo(() => {
    switch (filter) {
      case "active":
        return todos.filter((t) => !t.completed);
      case "completed":
        return todos.filter((t) => t.completed);
      default:
        return todos;
    }
  }, [todos, filter]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    dispatch({ type: "add", text: input.trim() });
    setInput("");
  };

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: 20 }}>
      <h1>Todo App</h1>

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add a todo..."
        />
        <button type="submit">Add</button>
      </form>

      <div style={{ margin: "10px 0" }}>
        {["all", "active", "completed"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{ fontWeight: filter === f ? "bold" : "normal", marginRight: 5 }}
          >
            {f}
          </button>
        ))}
      </div>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {filteredTodos.map((todo) => (
          <li key={todo.id} style={{ display: "flex", alignItems: "center", gap: 8, padding: 4 }}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => dispatch({ type: "toggle", id: todo.id })}
            />
            <span style={{ textDecoration: todo.completed ? "line-through" : "none", flex: 1 }}>
              {todo.text}
            </span>
            <button onClick={() => dispatch({ type: "delete", id: todo.id })}>X</button>
          </li>
        ))}
      </ul>

      <p>{todos.filter((t) => !t.completed).length} items left</p>
    </div>
  );
}

export default TodoApp;
```
