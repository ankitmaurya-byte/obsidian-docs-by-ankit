# Browser Storage

## Overview
```
storage_comparison:
  localStorage:
    capacity: "~5-10 MB per origin"
    persistence: "Permanent (until manually cleared)"
    scope: "Same origin (protocol + domain + port)"
    accessible_from: "Any tab/window on same origin"
    sent_with_requests: "No"
    api: "Synchronous"

  sessionStorage:
    capacity: "~5-10 MB per origin"
    persistence: "Until tab/window is closed"
    scope: "Same origin AND same tab"
    accessible_from: "Only the tab that created it"
    sent_with_requests: "No"
    api: "Synchronous"

  cookies:
    capacity: "~4 KB per cookie"
    persistence: "Until expiry date (or session if no expiry)"
    scope: "Domain + path based"
    accessible_from: "All tabs on matching domain"
    sent_with_requests: "Yes, automatically with every HTTP request"
    api: "Clunky string-based (document.cookie)"

  IndexedDB:
    capacity: "Hundreds of MB+ (browser-dependent)"
    persistence: "Permanent (until manually cleared)"
    scope: "Same origin"
    api: "Asynchronous, event-based"
    features: "Structured data, indexes, transactions, cursors"

  Cache_API:
    capacity: "Varies (large, typically limited by disk quota)"
    persistence: "Permanent (until manually cleared)"
    scope: "Same origin"
    api: "Promise-based"
    purpose: "Cache HTTP request/response pairs (Service Workers)"
```

## localStorage
```
localStorage:
  what: "Key-value store that persists data permanently in the browser"
  api:
    setItem: "localStorage.setItem(key, value)"
    getItem: "localStorage.getItem(key)  // returns null if not found"
    removeItem: "localStorage.removeItem(key)"
    clear: "localStorage.clear()  // removes all items"
    key: "localStorage.key(index)  // key name by index"
    length: "localStorage.length  // number of items"
  limitations:
    - Synchronous (blocks main thread)
    - Stores only strings (must JSON.stringify objects)
    - No expiration mechanism (must implement manually)
    - Accessible to any JS on the same origin (XSS risk)
  when_to_use:
    - User preferences (theme, language, layout)
    - Non-sensitive cached data
    - Draft content (auto-save form)
```

```javascript
// Basic usage
localStorage.setItem("theme", "dark");
const theme = localStorage.getItem("theme"); // "dark"
localStorage.removeItem("theme");

// Storing objects (must serialize)
const user = { name: "Ankit", preferences: { lang: "en" } };
localStorage.setItem("user", JSON.stringify(user));

const stored = JSON.parse(localStorage.getItem("user"));
console.log(stored.name); // "Ankit"

// Safe getter with fallback
function getFromStorage(key, fallback = null) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : fallback;
  } catch {
    return fallback;
  }
}

// Storage with expiration (manual implementation)
function setWithExpiry(key, value, ttlMs) {
  const item = {
    value,
    expiry: Date.now() + ttlMs,
  };
  localStorage.setItem(key, JSON.stringify(item));
}

function getWithExpiry(key) {
  const itemStr = localStorage.getItem(key);
  if (!itemStr) return null;

  const item = JSON.parse(itemStr);
  if (Date.now() > item.expiry) {
    localStorage.removeItem(key);
    return null;
  }
  return item.value;
}

// Set data that expires in 1 hour
setWithExpiry("cache:posts", postsData, 60 * 60 * 1000);

// Listen for storage changes (across tabs)
window.addEventListener("storage", (e) => {
  console.log(`Key: ${e.key}, Old: ${e.oldValue}, New: ${e.newValue}`);
});
```

## sessionStorage
```
sessionStorage:
  what: "Key-value store that persists data only for the current browser tab session"
  api: "Same as localStorage (setItem, getItem, removeItem, clear)"
  difference_from_localStorage:
    - Data cleared when tab is closed
    - Not shared between tabs (even same URL)
    - Survives page refreshes within same tab
    - New tab = new session (no data carried over)
  when_to_use:
    - Form wizard state (multi-step forms)
    - One-time notifications (show once per session)
    - Temporary UI state
    - Scroll position for back navigation
```

```javascript
// Multi-step form state
function saveFormStep(step, data) {
  const formData = JSON.parse(sessionStorage.getItem("wizardForm") || "{}");
  formData[`step${step}`] = data;
  sessionStorage.setItem("wizardForm", JSON.stringify(formData));
}

function getFormData() {
  return JSON.parse(sessionStorage.getItem("wizardForm") || "{}");
}

// On form completion
function submitForm() {
  const allData = getFormData();
  fetch("/api/submit", { method: "POST", body: JSON.stringify(allData) });
  sessionStorage.removeItem("wizardForm"); // cleanup
}

// One-time notification
function showWelcomeBanner() {
  if (sessionStorage.getItem("welcomeShown")) return;
  // show banner...
  sessionStorage.setItem("welcomeShown", "true");
}

// Save and restore scroll position
window.addEventListener("beforeunload", () => {
  sessionStorage.setItem("scrollY", window.scrollY.toString());
});

window.addEventListener("load", () => {
  const savedY = sessionStorage.getItem("scrollY");
  if (savedY) window.scrollTo(0, parseInt(savedY));
});
```

## Cookies
```
cookies:
  what: "Small pieces of data stored in the browser and sent with every HTTP request to the matching domain"
  attributes:
    Name_Value: "The cookie data (key=value)"
    Domain: "Which domain(s) receive the cookie"
    Path: "URL path the cookie is valid for (default: current path)"
    Expires_Max-Age: "When the cookie expires (omit = session cookie, deleted on browser close)"
    HttpOnly: "Cannot be accessed via JavaScript (document.cookie) - prevents XSS theft"
    Secure: "Only sent over HTTPS"
    SameSite:
      Strict: "Cookie only sent on same-site requests (no cross-site)"
      Lax: "Sent on same-site + top-level navigations from other sites (default)"
      None: "Sent on all requests (requires Secure flag)"

  security_best_practices:
    - Always set HttpOnly for auth cookies (prevents JS access)
    - Always set Secure (HTTPS only)
    - Use SameSite=Lax or Strict to prevent CSRF
    - Set short expiration for sensitive cookies
    - Scope cookies to specific paths when possible
```

```javascript
// Setting cookies (client-side - NOT recommended for auth)
document.cookie = "theme=dark; path=/; max-age=31536000"; // 1 year
document.cookie = "lang=en; path=/; max-age=31536000";

// Reading cookies (returns all cookies as one string)
function getCookie(name) {
  const cookies = document.cookie.split("; ");
  const cookie = cookies.find((c) => c.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.split("=")[1]) : null;
}

getCookie("theme"); // "dark"

// Delete cookie (set max-age to 0)
document.cookie = "theme=; path=/; max-age=0";

// Server-side cookie (Express.js example - proper auth cookies)
// HttpOnly cookies cannot be read by JavaScript - this is the correct approach
app.post("/login", (req, res) => {
  const token = generateToken(req.body.user);

  res.cookie("session", token, {
    httpOnly: true,    // not accessible via document.cookie
    secure: true,      // HTTPS only
    sameSite: "lax",   // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days in ms
    path: "/",
  });

  res.json({ message: "Logged in" });
});

// Clear server cookie
app.post("/logout", (req, res) => {
  res.clearCookie("session", { httpOnly: true, secure: true, sameSite: "lax" });
  res.json({ message: "Logged out" });
});
```

## Cookie vs Token Authentication
```
cookie_vs_token_auth:
  cookie_based:
    flow:
      1: "User logs in with credentials"
      2: "Server creates session, stores in DB/memory, sends session ID as HttpOnly cookie"
      3: "Browser automatically sends cookie with every request"
      4: "Server validates session ID on each request"
    pros:
      - HttpOnly prevents XSS token theft
      - Automatic - browser handles sending
      - Server can revoke sessions instantly
    cons:
      - Requires server-side session storage
      - CSRF vulnerability (mitigated with SameSite + CSRF tokens)
      - Harder to scale (sticky sessions or shared session store)

  token_based_jwt:
    flow:
      1: "User logs in with credentials"
      2: "Server creates JWT, sends in response body"
      3: "Client stores in memory (or localStorage) and sends in Authorization header"
      4: "Server validates JWT signature on each request"
    pros:
      - Stateless (no server-side session storage)
      - Works across domains/services
      - Easy to scale
    cons:
      - Stored in localStorage = XSS can steal it
      - Cannot be revoked easily (until expiry)
      - Token size grows with claims

  recommended:
    - "Use HttpOnly cookies for web apps (best security)"
    - "Use tokens for APIs consumed by mobile/third-party apps"
    - "Best of both: store JWT in HttpOnly cookie (server sets, browser sends)"
```

## IndexedDB
```
indexeddb:
  what: "Low-level asynchronous API for storing large amounts of structured data in the browser"
  features:
    - Stores JS objects directly (no serialization needed)
    - Supports indexes for fast queries
    - Transactional (all-or-nothing)
    - Supports cursors for iterating large datasets
    - Much larger storage limits than localStorage
  concepts:
    database: "Top-level container, has a name and version"
    object_store: "Like a table - holds records"
    index: "Secondary key for fast lookups"
    transaction: "Groups operations (readonly or readwrite)"
    cursor: "Iterator for walking through records"
  when_to_use:
    - Offline-first applications
    - Large datasets (files, blobs, complex objects)
    - Full-text search indexes
    - Caching API responses for offline use
```

```javascript
// Open database
function openDB(name, version = 1) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, version);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create object store (like a table)
      if (!db.objectStoreNames.contains("users")) {
        const store = db.createObjectStore("users", { keyPath: "id", autoIncrement: true });
        store.createIndex("email", "email", { unique: true });
        store.createIndex("name", "name", { unique: false });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// Add record
async function addUser(user) {
  const db = await openDB("myApp");
  const tx = db.transaction("users", "readwrite");
  const store = tx.objectStore("users");
  store.add(user);
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

// Get by key
async function getUser(id) {
  const db = await openDB("myApp");
  const tx = db.transaction("users", "readonly");
  const store = tx.objectStore("users");
  const request = store.get(id);
  return new Promise((resolve) => {
    request.onsuccess = () => resolve(request.result);
  });
}

// Get by index
async function getUserByEmail(email) {
  const db = await openDB("myApp");
  const tx = db.transaction("users", "readonly");
  const store = tx.objectStore("users");
  const index = store.index("email");
  const request = index.get(email);
  return new Promise((resolve) => {
    request.onsuccess = () => resolve(request.result);
  });
}

// Get all
async function getAllUsers() {
  const db = await openDB("myApp");
  const tx = db.transaction("users", "readonly");
  const store = tx.objectStore("users");
  const request = store.getAll();
  return new Promise((resolve) => {
    request.onsuccess = () => resolve(request.result);
  });
}

// Usage
await addUser({ name: "Ankit", email: "ankit@example.com", age: 25 });
const user = await getUserByEmail("ankit@example.com");

// Tip: Use 'idb' library for a cleaner Promise-based wrapper
// npm install idb
import { openDB } from "idb";
const db = await openDB("myApp", 1, {
  upgrade(db) {
    db.createObjectStore("users", { keyPath: "id", autoIncrement: true });
  },
});
await db.add("users", { name: "Ankit" });
const all = await db.getAll("users");
```

## Cache API
```
cache_api:
  what: "API for caching HTTP request/response pairs, primarily used with Service Workers"
  features:
    - Promise-based
    - Stores full Request/Response objects
    - Works with Service Workers for offline support
    - Multiple named caches
  methods:
    caches.open: "Open or create a named cache"
    cache.put: "Store a request/response pair"
    cache.match: "Find matching cached response"
    cache.add: "Fetch and cache a URL"
    cache.addAll: "Fetch and cache multiple URLs"
    cache.delete: "Remove a cached entry"
    cache.keys: "List all cached requests"
  when_to_use:
    - Progressive Web Apps (PWA)
    - Offline-first strategies
    - Caching static assets
    - API response caching
```

```javascript
// Cache static assets
async function precacheAssets() {
  const cache = await caches.open("static-v1");
  await cache.addAll([
    "/",
    "/index.html",
    "/styles.css",
    "/app.js",
    "/logo.png",
  ]);
}

// Cache-first strategy (check cache, fallback to network)
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  const cache = await caches.open("dynamic-v1");
  cache.put(request, response.clone()); // clone because response can only be consumed once
  return response;
}

// Network-first strategy (try network, fallback to cache)
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    const cache = await caches.open("dynamic-v1");
    cache.put(request, response.clone());
    return response;
  } catch {
    return caches.match(request); // offline fallback
  }
}

// Service Worker example
self.addEventListener("fetch", (event) => {
  if (event.request.url.includes("/api/")) {
    event.respondWith(networkFirst(event.request)); // API: network first
  } else {
    event.respondWith(cacheFirst(event.request)); // Assets: cache first
  }
});

// Clean old caches on activation
self.addEventListener("activate", (event) => {
  const currentCaches = ["static-v2", "dynamic-v1"];
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((name) => !currentCaches.includes(name))
          .map((name) => caches.delete(name))
      )
    )
  );
});
```

## When to Use Each
```
decision_guide:
  user_preferences:
    storage: localStorage
    reason: "Persists across sessions, small data, no security concern"
    example: "Theme, language, UI settings"

  form_wizard_state:
    storage: sessionStorage
    reason: "Only needed for current session, lost on tab close"
    example: "Multi-step form, temporary selections"

  authentication:
    storage: "HttpOnly cookie (set by server)"
    reason: "Not accessible to JS (XSS-safe), sent automatically"
    example: "Session ID, JWT in cookie"

  user_tracking_consent:
    storage: Cookie
    reason: "Needs to be sent to server, has expiry, cross-page"
    example: "Cookie consent, A/B test group"

  large_offline_data:
    storage: IndexedDB
    reason: "Large capacity, structured data, async"
    example: "Offline-first app data, file storage, search index"

  static_asset_caching:
    storage: Cache API
    reason: "Designed for HTTP request/response caching"
    example: "PWA offline assets, API response caching"
```

## Storage Limits
```
storage_limits:
  localStorage: "~5-10 MB per origin (varies by browser)"
  sessionStorage: "~5-10 MB per origin"
  cookies: "~4 KB per cookie, ~80 cookies per domain"
  IndexedDB: "Dynamic - typically up to 50% of free disk space (with user prompt)"
  Cache_API: "Dynamic - shares quota with IndexedDB"

  checking_quota:
    api: "navigator.storage.estimate()"
    returns: "{ usage: bytes_used, quota: bytes_available }"

  storage_eviction:
    when: "Browser is low on disk space"
    order: "LRU - least recently used origins evicted first"
    persistent: "navigator.storage.persist() - request persistent storage (won't be evicted)"
```

```javascript
// Check available storage
async function checkStorage() {
  if (navigator.storage && navigator.storage.estimate) {
    const { usage, quota } = await navigator.storage.estimate();
    console.log(`Using ${(usage / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Quota: ${(quota / 1024 / 1024).toFixed(2)} MB`);
    console.log(`${((usage / quota) * 100).toFixed(1)}% used`);
  }
}

// Request persistent storage (won't be evicted)
async function requestPersistence() {
  if (navigator.storage && navigator.storage.persist) {
    const granted = await navigator.storage.persist();
    console.log(granted ? "Persistent storage granted" : "Not granted");
  }
}
```

## Security Considerations
```
security:
  xss_risks:
    localStorage: "Any JS on the page can read it - if XSS, attacker steals tokens"
    sessionStorage: "Same as localStorage"
    cookies_without_httponly: "document.cookie exposes them to XSS"
    cookies_with_httponly: "Safe from XSS - JS cannot access"

  csrf_risks:
    cookies: "Vulnerable - cookies sent automatically with requests"
    mitigation:
      - "SameSite=Lax or Strict"
      - "CSRF tokens (server generates, client sends in form/header)"
      - "Check Origin/Referer headers"
    localStorage_tokens: "Not vulnerable to CSRF (must be explicitly added to requests)"

  best_practices:
    - Never store secrets in localStorage/sessionStorage
    - Use HttpOnly + Secure + SameSite for auth cookies
    - Sanitize all user input to prevent XSS
    - Set Content-Security-Policy headers
    - Use short-lived tokens with refresh token rotation
    - Encrypt sensitive data before storing
    - Clear sensitive data on logout
```

```javascript
// Secure pattern: HttpOnly cookie + CSRF token
// Server sets auth as HttpOnly cookie (JS can't touch it)
// Server also provides CSRF token in a non-HttpOnly cookie or meta tag

// Client reads CSRF token and includes in requests
function secureFetch(url, options = {}) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

  return fetch(url, {
    ...options,
    credentials: "include", // send cookies
    headers: {
      ...options.headers,
      "X-CSRF-Token": csrfToken,
      "Content-Type": "application/json",
    },
  });
}

// Clear all sensitive data on logout
function logout() {
  localStorage.clear();
  sessionStorage.clear();
  // HttpOnly cookies cleared by server response
  fetch("/api/logout", { method: "POST", credentials: "include" });
}
```
