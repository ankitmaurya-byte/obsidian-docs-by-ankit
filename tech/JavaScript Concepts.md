# JavaScript Concepts

## Event Loop
```
event_loop:
  what: Mechanism that allows JS to perform non-blocking operations despite being single-threaded
  how_it_works:
    - Call Stack: Executes synchronous code (LIFO)
    - Web APIs: Browser-provided async operations (setTimeout, fetch, DOM events)
    - Callback Queue (Task Queue): Holds callbacks from setTimeout, setInterval, I/O
    - Microtask Queue: Holds Promise callbacks (.then, .catch), MutationObserver, queueMicrotask
    - Event Loop: Continuously checks if call stack is empty, then processes microtasks first, then one task from callback queue

  execution_order:
    1: Synchronous code on call stack
    2: All microtasks (Promises, queueMicrotask)
    3: One macrotask (setTimeout, setInterval, I/O)
    4: All microtasks again
    5: Render (if needed)
    6: Repeat from step 3
```

```javascript
// Event loop demonstration
console.log("1 - synchronous");

setTimeout(() => console.log("2 - macrotask"), 0);

Promise.resolve().then(() => console.log("3 - microtask"));

queueMicrotask(() => console.log("4 - microtask"));

console.log("5 - synchronous");

// Output order: 1, 5, 3, 4, 2
// Sync first, then all microtasks, then macrotask
```

## Closures
```
closures:
  what: A function that retains access to its outer (enclosing) scope variables even after the outer function has returned
  how_it_works:
    - When a function is created, it captures a reference to its lexical environment
    - The inner function "closes over" the variables from the outer scope
    - Garbage collector keeps those variables alive as long as the closure exists
  use_cases:
    - Data privacy / encapsulation
    - Factory functions
    - Partial application and currying
    - Maintaining state in callbacks
```

```javascript
// Basic closure
function createCounter() {
  let count = 0; // private variable
  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count,
  };
}

const counter = createCounter();
counter.increment(); // 1
counter.increment(); // 2
counter.getCount();  // 2
// count is not accessible directly - only through returned methods

// Closure with loop (common gotcha)
// Problem: var is function-scoped
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100); // prints 3, 3, 3
}

// Fix 1: use let (block-scoped)
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100); // prints 0, 1, 2
}

// Fix 2: IIFE creates new scope
for (var i = 0; i < 3; i++) {
  ((j) => {
    setTimeout(() => console.log(j), 100); // prints 0, 1, 2
  })(i);
}

// Practical: function factory
function multiply(x) {
  return (y) => x * y;
}
const double = multiply(2);
const triple = multiply(3);
double(5); // 10
triple(5); // 15
```

## Promises
```
promises:
  what: An object representing the eventual completion or failure of an async operation
  states:
    pending: Initial state, neither fulfilled nor rejected
    fulfilled: Operation completed successfully (.then handler runs)
    rejected: Operation failed (.catch handler runs)
    settled: Either fulfilled or rejected (finally runs)
  key_methods:
    Promise.all: Waits for all promises, rejects if any one rejects
    Promise.allSettled: Waits for all to settle, never rejects, returns status of each
    Promise.race: Resolves/rejects with the first settled promise
    Promise.any: Resolves with first fulfilled, rejects only if all reject (AggregateError)
    Promise.resolve: Creates an already-resolved promise
    Promise.reject: Creates an already-rejected promise
```

```javascript
// Creating a promise
function fetchUser(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id > 0) resolve({ id, name: "Ankit" });
      else reject(new Error("Invalid ID"));
    }, 1000);
  });
}

// Chaining
fetchUser(1)
  .then((user) => {
    console.log(user.name);
    return fetchUser(2); // return another promise
  })
  .then((user2) => console.log(user2))
  .catch((err) => console.error(err.message))
  .finally(() => console.log("Done"));

// Promise.all - parallel execution, fail-fast
const [users, posts, comments] = await Promise.all([
  fetch("/api/users").then((r) => r.json()),
  fetch("/api/posts").then((r) => r.json()),
  fetch("/api/comments").then((r) => r.json()),
]);

// Promise.allSettled - get results of all regardless of failure
const results = await Promise.allSettled([
  fetch("/api/fast"),
  fetch("/api/might-fail"),
  fetch("/api/slow"),
]);
results.forEach((r) => {
  if (r.status === "fulfilled") console.log(r.value);
  else console.log("Failed:", r.reason);
});

// Promise.race - timeout pattern
const result = await Promise.race([
  fetch("/api/data"),
  new Promise((_, reject) =>
    setTimeout(() => reject(new Error("Timeout")), 5000)
  ),
]);
```

## Async/Await
```
async_await:
  what: Syntactic sugar over Promises that makes async code look synchronous
  how_it_works:
    - async keyword before a function makes it return a Promise
    - await pauses execution inside async function until the Promise settles
    - Does NOT block the main thread (other code continues running)
  error_handling: Use try/catch blocks instead of .catch()
  gotchas:
    - await only works inside async functions (or top-level in ES modules)
    - Forgetting await returns a Promise object instead of its value
    - Sequential awaits when parallel is intended (use Promise.all)
```

```javascript
// Basic async/await
async function getUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const user = await response.json();
    return user;
  } catch (error) {
    console.error("Failed to fetch user:", error.message);
    throw error; // re-throw to let caller handle
  }
}

// Sequential vs Parallel
async function sequential() {
  const user = await fetchUser(1);   // waits 1s
  const posts = await fetchPosts(1); // waits another 1s
  // Total: ~2 seconds
}

async function parallel() {
  const [user, posts] = await Promise.all([
    fetchUser(1),
    fetchPosts(1),
  ]);
  // Total: ~1 second (runs concurrently)
}

// Async iteration
async function processItems(urls) {
  for (const url of urls) {
    const data = await fetch(url).then((r) => r.json());
    console.log(data);
  }
}

// Top-level await (ES modules only)
const config = await fetch("/config.json").then((r) => r.json());
```

## Prototypes
```
prototypes:
  what: The mechanism by which JavaScript objects inherit features from one another
  how_it_works:
    - Every JS object has an internal [[Prototype]] link to another object
    - When accessing a property, JS walks up the prototype chain until found or null
    - Object.prototype is the top of the chain (its [[Prototype]] is null)
    - Functions have a .prototype property used when called with new
  key_methods:
    Object.create(proto): Creates object with specified prototype
    Object.getPrototypeOf(obj): Returns the prototype of obj
    obj.hasOwnProperty(key): Checks if property is directly on obj (not inherited)
    instanceof: Checks if prototype chain includes Constructor.prototype
```

```javascript
// Prototype chain
const animal = {
  speak() {
    return `${this.name} makes a sound`;
  },
};

const dog = Object.create(animal);
dog.name = "Rex";
dog.bark = function () {
  return `${this.name} barks`;
};

dog.speak(); // "Rex makes a sound" (inherited from animal)
dog.bark();  // "Rex barks" (own method)

dog.hasOwnProperty("name");  // true
dog.hasOwnProperty("speak"); // false (inherited)

// Constructor function pattern
function Person(name, age) {
  this.name = name;
  this.age = age;
}
Person.prototype.greet = function () {
  return `Hi, I'm ${this.name}`;
};

const p = new Person("Ankit", 25);
p.greet();                  // "Hi, I'm Ankit"
p instanceof Person;        // true
Object.getPrototypeOf(p) === Person.prototype; // true

// ES6 class (syntactic sugar over prototypes)
class Animal {
  constructor(name) {
    this.name = name;
  }
  speak() {
    return `${this.name} makes a sound`;
  }
}

class Dog extends Animal {
  bark() {
    return `${this.name} barks`;
  }
}

const d = new Dog("Rex");
d.speak(); // "Rex makes a sound"
d.bark();  // "Rex barks"
```

## this Keyword
```
this_keyword:
  what: A special keyword that refers to the object that is executing the current function
  rules:
    global_context: "window (browser) or global (Node), undefined in strict mode"
    object_method: "this = the object that owns the method"
    regular_function: "this = caller (or undefined in strict mode)"
    arrow_function: "this = lexically inherited from enclosing scope (never changes)"
    new_keyword: "this = the newly created object"
    call_apply_bind: "this = explicitly set to first argument"
    event_handler: "this = the element that received the event (unless arrow function)"
  priority_order:
    1: new binding
    2: explicit binding (call, apply, bind)
    3: implicit binding (object method)
    4: default binding (global or undefined)
```

```javascript
// Object method
const user = {
  name: "Ankit",
  greet() {
    return `Hi, ${this.name}`;
  },
};
user.greet(); // "Hi, Ankit"

// Lost context
const greet = user.greet;
greet(); // "Hi, undefined" (this is global/undefined)

// Arrow function inherits this
const user2 = {
  name: "Ankit",
  greet: () => `Hi, ${this.name}`, // this = outer scope, NOT user2
  delayedGreet() {
    setTimeout(() => {
      console.log(this.name); // "Ankit" - arrow inherits from delayedGreet
    }, 100);
  },
};

// call, apply, bind
function introduce(greeting) {
  return `${greeting}, I'm ${this.name}`;
}
introduce.call({ name: "Ankit" }, "Hello");   // "Hello, I'm Ankit"
introduce.apply({ name: "Ankit" }, ["Hello"]); // "Hello, I'm Ankit"

const bound = introduce.bind({ name: "Ankit" });
bound("Hey"); // "Hey, I'm Ankit"

// new keyword
function Car(make) {
  this.make = make;  // this = new empty object
}
const car = new Car("Toyota"); // { make: "Toyota" }
```

## Hoisting
```
hoisting:
  what: JavaScript moves declarations to the top of their scope during compilation phase
  behavior:
    var: Declaration hoisted, initialized to undefined
    let_const: Declaration hoisted but NOT initialized (Temporal Dead Zone until declaration line)
    function_declaration: Fully hoisted (both declaration and body)
    function_expression: Only var declaration hoisted (as undefined), function body NOT hoisted
    class: Hoisted but NOT initialized (TDZ like let/const)
```

```javascript
// var hoisting
console.log(x); // undefined (declaration hoisted, value not)
var x = 5;

// let/const - Temporal Dead Zone
console.log(y); // ReferenceError: Cannot access 'y' before initialization
let y = 10;

// Function declaration - fully hoisted
greet(); // "Hello!" - works fine
function greet() {
  console.log("Hello!");
}

// Function expression - NOT fully hoisted
sayHi(); // TypeError: sayHi is not a function
var sayHi = function () {
  console.log("Hi!");
};
```

## var, let, const
```
var_let_const:
  var:
    scope: Function-scoped
    hoisting: Hoisted and initialized to undefined
    reassignment: Yes
    redeclaration: Yes (in same scope)
    creates_window_property: Yes (in global scope)

  let:
    scope: Block-scoped
    hoisting: Hoisted but NOT initialized (TDZ)
    reassignment: Yes
    redeclaration: No (SyntaxError)
    creates_window_property: No

  const:
    scope: Block-scoped
    hoisting: Hoisted but NOT initialized (TDZ)
    reassignment: No (TypeError)
    redeclaration: No (SyntaxError)
    note: "Object/array contents CAN be mutated, only the binding is constant"

  best_practice:
    - Use const by default
    - Use let when reassignment is needed
    - Never use var in modern code
```

```javascript
// Scope difference
if (true) {
  var a = 1;   // leaks out of block
  let b = 2;   // stays in block
  const c = 3; // stays in block
}
console.log(a); // 1
console.log(b); // ReferenceError
console.log(c); // ReferenceError

// const with objects - contents are mutable
const user = { name: "Ankit" };
user.name = "Updated";  // OK - mutating property
user.age = 25;           // OK - adding property
user = {};               // TypeError - can't reassign binding
```

## Spread and Rest Operators
```
spread_rest:
  spread:
    what: Expands an iterable into individual elements
    syntax: "...iterable"
    use_cases:
      - Copy arrays/objects (shallow)
      - Merge arrays/objects
      - Pass array elements as function arguments

  rest:
    what: Collects remaining elements into an array
    syntax: "...paramName"
    use_cases:
      - Gather remaining function arguments
      - Destructure remaining properties
```

```javascript
// Spread - arrays
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const merged = [...arr1, ...arr2];       // [1, 2, 3, 4, 5, 6]
const copy = [...arr1];                   // [1, 2, 3] (shallow copy)
Math.max(...arr1);                        // 3

// Spread - objects
const defaults = { theme: "dark", lang: "en" };
const userPrefs = { lang: "fr" };
const config = { ...defaults, ...userPrefs }; // { theme: "dark", lang: "fr" }

// Rest - function parameters
function sum(...numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}
sum(1, 2, 3, 4); // 10

// Rest - destructuring
const [first, second, ...remaining] = [1, 2, 3, 4, 5];
// first=1, second=2, remaining=[3,4,5]

const { name, ...otherProps } = { name: "Ankit", age: 25, city: "Delhi" };
// name="Ankit", otherProps={ age: 25, city: "Delhi" }
```

## Destructuring
```
destructuring:
  what: Syntax for extracting values from arrays or properties from objects into variables
  types:
    array_destructuring: "Positional - based on index"
    object_destructuring: "Named - based on property name"
  features:
    - Default values
    - Renaming (aliasing)
    - Nested destructuring
    - Skipping elements (arrays)
    - Computed property names
```

```javascript
// Object destructuring
const user = { name: "Ankit", age: 25, city: "Delhi" };
const { name, age } = user;

// Renaming
const { name: userName, age: userAge } = user;

// Default values
const { name, role = "user" } = user; // role defaults to "user"

// Nested
const data = { user: { name: "Ankit", address: { city: "Delhi" } } };
const { user: { name, address: { city } } } = data;

// Array destructuring
const [a, b, c] = [1, 2, 3];

// Skip elements
const [first, , third] = [1, 2, 3]; // first=1, third=3

// Swap variables
let x = 1, y = 2;
[x, y] = [y, x]; // x=2, y=1

// Function parameter destructuring
function createUser({ name, age, role = "user" }) {
  return { name, age, role };
}
createUser({ name: "Ankit", age: 25 });
```

## map, filter, reduce
```
array_methods:
  map:
    what: Creates a new array by transforming each element
    returns: New array of same length
    does_not_mutate: true

  filter:
    what: Creates a new array with elements that pass a test
    returns: New array (possibly shorter)
    does_not_mutate: true

  reduce:
    what: Reduces an array to a single value by applying a function cumulatively
    returns: Single accumulated value (any type)
    does_not_mutate: true
    parameters: "callback(accumulator, currentValue, index, array), initialValue"
```

```javascript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// map - transform each element
const doubled = numbers.map((n) => n * 2);
// [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

// filter - keep elements passing test
const evens = numbers.filter((n) => n % 2 === 0);
// [2, 4, 6, 8, 10]

// reduce - accumulate into single value
const sum = numbers.reduce((acc, n) => acc + n, 0);
// 55

// Chaining them together
const users = [
  { name: "Ankit", age: 25, active: true },
  { name: "Bob", age: 30, active: false },
  { name: "Charlie", age: 20, active: true },
];

const activeNames = users
  .filter((u) => u.active)
  .map((u) => u.name)
  .reduce((str, name, i) => (i === 0 ? name : `${str}, ${name}`), "");
// "Ankit, Charlie"

// reduce - group by
const grouped = users.reduce((acc, user) => {
  const key = user.active ? "active" : "inactive";
  acc[key] = acc[key] || [];
  acc[key].push(user);
  return acc;
}, {});
// { active: [{Ankit}, {Charlie}], inactive: [{Bob}] }

// reduce - build object from array
const nameAgeMap = users.reduce((acc, u) => {
  acc[u.name] = u.age;
  return acc;
}, {});
// { Ankit: 25, Bob: 30, Charlie: 20 }
```

## Modules (ESM vs CommonJS)
```
modules:
  esm:
    full_name: ECMAScript Modules
    syntax_import: "import { foo } from './module.js'"
    syntax_export: "export const foo = 42"
    default_export: "export default function() {}"
    loading: Static (resolved at parse time, enables tree shaking)
    execution: Asynchronous
    file_extension: ".mjs or .js with type:module in package.json"
    top_level_await: Supported
    this_value: undefined

  commonjs:
    syntax_import: "const foo = require('./module')"
    syntax_export: "module.exports = { foo }"
    loading: Dynamic (resolved at runtime)
    execution: Synchronous
    file_extension: ".cjs or .js (default in Node)"
    top_level_await: Not supported
    this_value: module.exports

  when_to_use:
    esm: "Modern projects, frontend, new Node.js apps, tree-shakeable libraries"
    commonjs: "Legacy Node.js projects, scripts that need dynamic requires"
```

```javascript
// ESM - Named exports
// math.js
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;

// app.js
import { add, subtract } from "./math.js";
import * as math from "./math.js"; // namespace import
math.add(1, 2);

// ESM - Default export
// logger.js
export default class Logger {
  log(msg) { console.log(msg); }
}

// app.js
import Logger from "./logger.js"; // name can be anything

// ESM - Re-export
export { add, subtract } from "./math.js";
export { default as Logger } from "./logger.js";

// CommonJS
// math.js
const add = (a, b) => a + b;
module.exports = { add };

// app.js
const { add } = require("./math");

// Dynamic import (both systems)
const module = await import("./heavy-module.js");
module.doSomething();
```

## Generators
```
generators:
  what: Functions that can be paused and resumed, yielding multiple values over time
  syntax: "function* generatorName() { yield value; }"
  how_it_works:
    - Calling a generator function returns a Generator object (an iterator)
    - Calling .next() runs until the next yield and returns { value, done }
    - yield pauses execution and sends value out
    - .next(val) can send a value back into the generator
    - .return(val) forces generator to finish
    - .throw(err) throws error inside generator
  use_cases:
    - Lazy iteration (infinite sequences)
    - Custom iterables
    - Async flow control (before async/await existed)
    - Stateful iteration
```

```javascript
// Basic generator
function* range(start, end, step = 1) {
  for (let i = start; i < end; i += step) {
    yield i;
  }
}

const nums = range(0, 10, 2);
nums.next(); // { value: 0, done: false }
nums.next(); // { value: 2, done: false }

// Spread into array
[...range(0, 5)]; // [0, 1, 2, 3, 4]

// for...of works with generators
for (const n of range(0, 3)) {
  console.log(n); // 0, 1, 2
}

// Infinite sequence (lazy - only generates on demand)
function* fibonacci() {
  let a = 0, b = 1;
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

const fib = fibonacci();
fib.next().value; // 0
fib.next().value; // 1
fib.next().value; // 1
fib.next().value; // 2
fib.next().value; // 3

// Two-way communication
function* conversation() {
  const name = yield "What is your name?";
  const age = yield `Hello ${name}! How old are you?`;
  return `${name} is ${age} years old`;
}

const chat = conversation();
chat.next();            // { value: "What is your name?", done: false }
chat.next("Ankit");     // { value: "Hello Ankit! How old are you?", done: false }
chat.next(25);          // { value: "Ankit is 25 years old", done: true }
```

## WeakMap and WeakSet
```
weak_collections:
  WeakMap:
    what: "Map where keys must be objects, and keys are held weakly (garbage collected when no other reference)"
    methods: "get, set, has, delete (NO size, NO iteration)"
    use_cases:
      - Store private data associated with objects
      - Cache computed results tied to object lifetime
      - DOM node metadata

  WeakSet:
    what: "Set that only holds objects weakly (garbage collected when no other reference)"
    methods: "add, has, delete (NO size, NO iteration)"
    use_cases:
      - Track if an object has been processed
      - Mark objects (visited, tagged)

  why_weak:
    - Does not prevent garbage collection of keys/values
    - No memory leaks when objects are discarded
    - Cannot be iterated (entries are non-deterministic due to GC)
```

```javascript
// WeakMap - private data
const privateData = new WeakMap();

class User {
  constructor(name, password) {
    this.name = name;
    privateData.set(this, { password }); // private, tied to object lifetime
  }
  checkPassword(input) {
    return privateData.get(this).password === input;
  }
}

let user = new User("Ankit", "secret123");
user.checkPassword("secret123"); // true
user = null; // password data is now eligible for GC

// WeakMap - caching
const cache = new WeakMap();

function expensiveComputation(obj) {
  if (cache.has(obj)) return cache.get(obj);
  const result = /* heavy work */ JSON.stringify(obj);
  cache.set(obj, result);
  return result;
}

// WeakSet - track processed items
const processed = new WeakSet();

function processOnce(obj) {
  if (processed.has(obj)) return;
  processed.add(obj);
  // do processing...
}
```

## Proxy
```
proxy:
  what: An object that wraps another object and intercepts/redefines fundamental operations
  syntax: "new Proxy(target, handler)"
  handler_traps:
    get: "Intercept property read"
    set: "Intercept property write"
    has: "Intercept 'in' operator"
    deleteProperty: "Intercept delete operator"
    apply: "Intercept function call"
    construct: "Intercept new operator"
    ownKeys: "Intercept Object.keys, for...in"
  use_cases:
    - Validation
    - Logging/debugging
    - Default values for missing properties
    - Data binding / reactivity (Vue 3 uses Proxy)
    - Access control
```

```javascript
// Validation proxy
const validator = {
  set(target, prop, value) {
    if (prop === "age" && (typeof value !== "number" || value < 0)) {
      throw new TypeError("Age must be a positive number");
    }
    target[prop] = value;
    return true;
  },
};

const user = new Proxy({}, validator);
user.name = "Ankit";  // OK
user.age = 25;         // OK
user.age = -1;         // TypeError: Age must be a positive number

// Default values for missing properties
const withDefaults = new Proxy(
  { name: "Ankit", role: "dev" },
  {
    get(target, prop) {
      return prop in target ? target[prop] : `No ${prop} found`;
    },
  }
);
withDefaults.name;    // "Ankit"
withDefaults.email;   // "No email found"

// Logging proxy
function createLogged(obj) {
  return new Proxy(obj, {
    get(target, prop) {
      console.log(`GET ${prop}`);
      return target[prop];
    },
    set(target, prop, value) {
      console.log(`SET ${prop} = ${value}`);
      target[prop] = value;
      return true;
    },
  });
}
```

## Symbol
```
symbol:
  what: A primitive type representing a unique, immutable identifier
  creation: "Symbol('description') - description is optional, for debugging only"
  uniqueness: "Symbol('a') !== Symbol('a') - every Symbol is unique"
  well_known_symbols:
    Symbol.iterator: Makes object iterable (for...of)
    Symbol.toPrimitive: Controls type conversion
    Symbol.hasInstance: Controls instanceof behavior
    Symbol.toStringTag: Controls Object.prototype.toString output
  Symbol.for:
    what: "Global Symbol registry - Symbol.for('key') returns same Symbol for same key"
    use: "Share Symbols across files/modules"
  use_cases:
    - Unique object property keys (no collisions)
    - Define protocols/interfaces (like Symbol.iterator)
    - Enum-like constants
    - Hide properties from normal iteration
```

```javascript
// Unique property keys
const ID = Symbol("id");
const user = {
  [ID]: 123,
  name: "Ankit",
};
user[ID];          // 123
Object.keys(user); // ["name"] - Symbol keys are hidden from normal iteration

// Symbol.for - global registry
const s1 = Symbol.for("app.id");
const s2 = Symbol.for("app.id");
s1 === s2; // true (same key in global registry)

// Custom iterator with Symbol.iterator
const range = {
  from: 1,
  to: 5,
  [Symbol.iterator]() {
    let current = this.from;
    const last = this.to;
    return {
      next() {
        return current <= last
          ? { value: current++, done: false }
          : { done: true };
      },
    };
  },
};

[...range]; // [1, 2, 3, 4, 5]
for (const n of range) console.log(n); // 1, 2, 3, 4, 5

// Enum-like usage
const Status = Object.freeze({
  PENDING: Symbol("pending"),
  ACTIVE: Symbol("active"),
  CLOSED: Symbol("closed"),
});
```
