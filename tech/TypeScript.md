# TypeScript

## What is TypeScript
```
overview:
  what: A strongly typed superset of JavaScript that compiles to plain JavaScript
  created_by: Microsoft (Anders Hejlsberg, 2012)
  key_benefits:
    - Static type checking at compile time (catch errors before runtime)
    - Better IDE support (autocompletion, refactoring, go-to-definition)
    - Self-documenting code through types
    - Gradual adoption (valid JS is valid TS)
  compilation: "TypeScript (.ts) -> tsc compiler -> JavaScript (.js)"
  file_extensions:
    .ts: TypeScript source
    .tsx: TypeScript with JSX (React)
    .d.ts: Type declaration files (no runtime code)
```

## Types - Primitives
```
primitive_types:
  string: "let name: string = 'Ankit'"
  number: "let age: number = 25  // integers and floats"
  boolean: "let active: boolean = true"
  null: "let empty: null = null"
  undefined: "let notSet: undefined = undefined"
  bigint: "let big: bigint = 100n"
  symbol: "let id: symbol = Symbol('id')"

  special_types:
    any: "Disables type checking (avoid when possible)"
    unknown: "Type-safe alternative to any (must narrow before use)"
    void: "Function returns nothing"
    never: "Function never returns (throws or infinite loop)"
```

```typescript
// Primitive examples
let name: string = "Ankit";
let age: number = 25;
let isActive: boolean = true;

// any vs unknown
let risky: any = "hello";
risky.nonExistentMethod(); // No error at compile time (dangerous)

let safe: unknown = "hello";
// safe.toUpperCase();     // Error: Object is of type 'unknown'
if (typeof safe === "string") {
  safe.toUpperCase();      // OK after narrowing
}

// void and never
function log(msg: string): void {
  console.log(msg);
}

function throwError(msg: string): never {
  throw new Error(msg);
}
```

## Union and Intersection Types
```
union_intersection:
  union:
    syntax: "type A = string | number"
    meaning: "Value can be ANY ONE of the listed types"
    use_case: "When a value could be multiple types"

  intersection:
    syntax: "type C = A & B"
    meaning: "Value must satisfy ALL listed types simultaneously"
    use_case: "Combining multiple types/interfaces into one"

  literal_types:
    what: "Exact values as types (not just string, but specific strings)"
    syntax: "type Direction = 'up' | 'down' | 'left' | 'right'"
```

```typescript
// Union types
type ID = string | number;

function printId(id: ID) {
  if (typeof id === "string") {
    console.log(id.toUpperCase()); // narrowed to string
  } else {
    console.log(id.toFixed(2));    // narrowed to number
  }
}

printId("abc");  // OK
printId(123);    // OK
printId(true);   // Error

// Intersection types
type HasName = { name: string };
type HasAge = { age: number };
type Person = HasName & HasAge;

const person: Person = { name: "Ankit", age: 25 }; // must have both

// Literal types
type Status = "active" | "inactive" | "pending";
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type DiceRoll = 1 | 2 | 3 | 4 | 5 | 6;

let status: Status = "active";   // OK
status = "unknown";               // Error
```

## Interfaces vs Types
```
interfaces_vs_types:
  interface:
    syntax: "interface User { name: string; }"
    extends: "interface Admin extends User { role: string; }"
    declaration_merging: "Yes - same interface name declared twice merges automatically"
    best_for: "Object shapes, class contracts, library APIs"

  type:
    syntax: "type User = { name: string; }"
    extends: "type Admin = User & { role: string; }"
    declaration_merging: "No - duplicate type name is an error"
    can_represent: "Unions, intersections, primitives, tuples, mapped types"
    best_for: "Complex types, unions, utility types"

  general_rule:
    - Use interface for object shapes and public APIs
    - Use type for unions, intersections, and complex compositions
    - Both work for most cases; be consistent in your project
```

```typescript
// Interface
interface User {
  id: number;
  name: string;
  email?: string; // optional
  readonly createdAt: Date; // can't be changed after creation
}

// Interface extension
interface Admin extends User {
  role: "admin" | "superadmin";
  permissions: string[];
}

// Declaration merging (interfaces only)
interface Config {
  apiUrl: string;
}
interface Config {
  timeout: number;
}
// Config is now { apiUrl: string; timeout: number }

// Type aliases
type ID = string | number;
type Coordinates = [number, number]; // tuple
type Callback = (data: string) => void; // function type

// Type intersection (like extends)
type Employee = User & {
  department: string;
  salary: number;
};

// Interface with index signature
interface Dictionary {
  [key: string]: string;
}

// Interface for function
interface SearchFunc {
  (query: string, limit?: number): Promise<Result[]>;
}
```

## Generics
```
generics:
  what: "Allow creating reusable components that work with multiple types while maintaining type safety"
  syntax: "function identity<T>(arg: T): T"
  key_concepts:
    type_parameter: "T, U, K, V are conventional names"
    constraints: "T extends SomeType - limits what T can be"
    default_type: "T = string - fallback type if not specified"
  use_cases:
    - Generic functions
    - Generic interfaces and classes
    - Generic utility types
    - Constraining one type param based on another
```

```typescript
// Generic function
function identity<T>(value: T): T {
  return value;
}
identity<string>("hello"); // explicit
identity(42);              // inferred as number

// Generic with constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
const user = { name: "Ankit", age: 25 };
getProperty(user, "name"); // string
getProperty(user, "foo");  // Error: "foo" is not in keyof User

// Generic interface
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

type UserResponse = ApiResponse<User>;
type PostResponse = ApiResponse<Post[]>;

// Generic class
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }
}

const numStack = new Stack<number>();
numStack.push(1);
numStack.push(2);
numStack.pop(); // 2

// Generic with default
interface PaginatedResult<T, M = Record<string, unknown>> {
  items: T[];
  total: number;
  page: number;
  meta: M;
}
```

## Enums
```
enums:
  what: "A way to define a set of named constants"
  types:
    numeric_enum: "Auto-incremented numbers starting from 0 (or custom start)"
    string_enum: "Each member has a string value (preferred for readability)"
    const_enum: "Compiled away entirely, inlined at usage (const enum)"
    heterogeneous: "Mix of string and number (avoid)"
  gotchas:
    - Numeric enums allow reverse mapping (value -> name) which can cause bugs
    - Enums generate runtime code (unlike most TS features)
    - const enums are fully erased at compile time
  alternative: "Union of string literals is often preferred in modern TS"
```

```typescript
// Numeric enum
enum Direction {
  Up,    // 0
  Down,  // 1
  Left,  // 2
  Right, // 3
}

// String enum (preferred)
enum Status {
  Active = "ACTIVE",
  Inactive = "INACTIVE",
  Pending = "PENDING",
}

function setStatus(status: Status) {
  console.log(status);
}
setStatus(Status.Active); // "ACTIVE"

// Const enum (inlined, no runtime object)
const enum Color {
  Red = "#ff0000",
  Green = "#00ff00",
  Blue = "#0000ff",
}
const bg = Color.Red; // compiled to: const bg = "#ff0000"

// Modern alternative: union of literals
type StatusAlt = "active" | "inactive" | "pending";
// Simpler, no runtime cost, works well with type narrowing
```

## Type Guards
```
type_guards:
  what: "Expressions that narrow a type within a conditional block"
  built_in:
    typeof: "typeof x === 'string'"
    instanceof: "x instanceof Date"
    in: "'name' in obj"
    equality: "x === null, x !== undefined"
    truthiness: "if (x) - narrows out null/undefined/0/empty string"
  custom:
    syntax: "function isFish(pet: Fish | Bird): pet is Fish"
    returns: "boolean, but tells TS the type is narrowed"
  discriminated_unions:
    what: "Union types with a common literal property used to discriminate"
    pattern: "switch on the discriminant property"
```

```typescript
// typeof guard
function padLeft(value: string, padding: string | number): string {
  if (typeof padding === "number") {
    return " ".repeat(padding) + value; // padding is number
  }
  return padding + value; // padding is string
}

// instanceof guard
function formatDate(date: string | Date): string {
  if (date instanceof Date) {
    return date.toISOString();
  }
  return new Date(date).toISOString();
}

// in guard
interface Fish { swim(): void; }
interface Bird { fly(): void; }

function move(animal: Fish | Bird) {
  if ("swim" in animal) {
    animal.swim(); // narrowed to Fish
  } else {
    animal.fly();  // narrowed to Bird
  }
}

// Custom type guard
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function process(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase()); // TS knows it's string
  }
}

// Discriminated union
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return (shape.base * shape.height) / 2;
  }
}
```

## Utility Types
```
utility_types:
  Partial<T>: "Makes all properties optional"
  Required<T>: "Makes all properties required"
  Readonly<T>: "Makes all properties readonly"
  Pick<T, K>: "Select subset of properties"
  Omit<T, K>: "Remove subset of properties"
  Record<K, V>: "Create object type with keys K and values V"
  Exclude<T, U>: "Remove types from union"
  Extract<T, U>: "Keep only types matching U from union"
  NonNullable<T>: "Remove null and undefined from type"
  ReturnType<T>: "Get return type of a function"
  Parameters<T>: "Get parameter types of a function as tuple"
  Awaited<T>: "Unwrap Promise type"
```

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

// Partial - all optional (great for update functions)
function updateUser(id: number, updates: Partial<User>) {
  // updates can have any subset of User properties
}
updateUser(1, { name: "New Name" }); // OK

// Pick - select specific properties
type UserPreview = Pick<User, "id" | "name">;
// { id: number; name: string }

// Omit - exclude specific properties
type CreateUserDTO = Omit<User, "id">;
// { name: string; email: string; age: number }

// Record - dictionary type
type UserRoles = Record<string, "admin" | "user" | "guest">;
const roles: UserRoles = {
  ankit: "admin",
  bob: "user",
};

// Readonly
const config: Readonly<{ apiUrl: string; timeout: number }> = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
};
// config.apiUrl = "new"; // Error: cannot assign to readonly

// ReturnType
function createUser() {
  return { id: 1, name: "Ankit" };
}
type CreatedUser = ReturnType<typeof createUser>;
// { id: number; name: string }

// Exclude and Extract
type AllEvents = "click" | "scroll" | "mousemove" | "keydown";
type MouseEvents = Extract<AllEvents, "click" | "mousemove">;
// "click" | "mousemove"
type NonMouseEvents = Exclude<AllEvents, "click" | "mousemove">;
// "scroll" | "keydown"
```

## Declaration Files
```
declaration_files:
  what: "Files ending in .d.ts that describe the types of existing JS code without implementation"
  purpose:
    - Provide types for JS libraries that don't have built-in types
    - Describe global variables, modules, or augmented types
  sources:
    DefinitelyTyped: "Community repo of type definitions (@types/xxx packages)"
    bundled: "Library ships its own .d.ts files"
    custom: "Write your own for untyped JS code"
  common_patterns:
    - "declare module 'module-name' { ... }"
    - "declare global { ... }"
    - "declare function, declare const, declare class"
```

```typescript
// custom.d.ts - declare types for an untyped JS module
declare module "untyped-lib" {
  export function doSomething(input: string): number;
  export interface Config {
    verbose: boolean;
    outputDir: string;
  }
}

// global.d.ts - extend global scope
declare global {
  interface Window {
    myApp: {
      version: string;
      config: Record<string, unknown>;
    };
  }
}

// Ambient declaration for a global variable
declare const API_URL: string;
declare function gtag(command: string, ...args: unknown[]): void;

// Module augmentation (extend existing module types)
import "express";
declare module "express" {
  interface Request {
    user?: { id: string; role: string };
  }
}
```

## tsconfig.json
```
tsconfig:
  what: "Configuration file for the TypeScript compiler"
  key_options:
    compilerOptions:
      target: "ES2020, ES2022, ESNext - JS version to compile to"
      module: "commonjs, ESNext, NodeNext - module system"
      lib: "['ES2020', 'DOM'] - available built-in type definitions"
      strict: "true - enables all strict checks (recommended)"
      outDir: "./dist - output directory for compiled JS"
      rootDir: "./src - root directory of source files"
      esModuleInterop: "true - fixes CommonJS/ESM import compatibility"
      moduleResolution: "node, bundler, NodeNext - how to resolve imports"
      baseUrl: ". - base for non-relative imports"
      paths: "Path aliases like @/* -> src/*"
      declaration: "true - generate .d.ts files"
      sourceMap: "true - generate source maps for debugging"
      skipLibCheck: "true - skip type checking of .d.ts files (faster builds)"
      forceConsistentCasingInFileNames: "true - prevent case-sensitivity issues"
      noEmit: "true - only type-check, don't produce output (for bundler setups)"
    include: "['src/**/*'] - files to include"
    exclude: "['node_modules', 'dist'] - files to exclude"
```

```json
// Recommended tsconfig.json for a modern project
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "sourceMap": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Mapped Types
```
mapped_types:
  what: "Create new types by transforming each property of an existing type"
  syntax: "{ [K in keyof T]: NewType }"
  modifiers:
    readonly: "Add or remove with + or -"
    optional: "Add or remove ? with + or -"
  built_in_mapped_types:
    - "Partial<T>, Required<T>, Readonly<T> are all mapped types internally"
```

```typescript
// Make all properties nullable
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

interface User {
  name: string;
  age: number;
}

type NullableUser = Nullable<User>;
// { name: string | null; age: number | null }

// How Partial works internally
type MyPartial<T> = {
  [K in keyof T]?: T[K];
};

// Remove readonly (using - modifier)
type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

// Transform property types based on key
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number }

// Filter properties by type
type OnlyStrings<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K];
};

type StringProps = OnlyStrings<{ name: string; age: number; email: string }>;
// { name: string; email: string }
```

## Conditional Types
```
conditional_types:
  what: "Types that choose between two types based on a condition"
  syntax: "T extends U ? X : Y"
  key_features:
    distributive: "When T is a union, condition is applied to each member separately"
    infer: "Extract type within a conditional type using 'infer' keyword"
  use_cases:
    - Unwrap types (extract inner type from wrapper)
    - Conditional return types
    - Type-level programming
```

```typescript
// Basic conditional type
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false

// Distributive over unions
type ToArray<T> = T extends any ? T[] : never;
type Result = ToArray<string | number>; // string[] | number[]

// Non-distributive (wrap in tuple)
type ToArrayND<T> = [T] extends [any] ? T[] : never;
type Result2 = ToArrayND<string | number>; // (string | number)[]

// infer keyword - extract types
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type A2 = UnwrapPromise<Promise<string>>; // string
type B2 = UnwrapPromise<number>;          // number

// Extract function return type (how ReturnType works)
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// Extract array element type
type ElementOf<T> = T extends (infer E)[] ? E : T;
type El = ElementOf<string[]>; // string

// Practical: make certain keys required
type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;

interface Config {
  host?: string;
  port?: number;
  debug?: boolean;
}

type ProdConfig = RequireKeys<Config, "host" | "port">;
// host and port are required, debug remains optional
```
