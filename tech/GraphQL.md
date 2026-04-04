# GraphQL

## What is GraphQL
```
overview:
  full_name: Graph Query Language
  type: Query language for APIs and runtime for executing queries
  created_by: Facebook (2012 internal, 2015 open-sourced)
  transport: HTTP (typically POST to single /graphql endpoint)
  format: JSON responses
  spec: graphql.org

key_features:
  - Single endpoint for all operations
  - Client specifies exact data shape needed
  - Strongly typed schema
  - No over-fetching or under-fetching
  - Introspectable (clients can query the schema itself)
  - Real-time updates via subscriptions
  - Versionless API (add fields, deprecate old ones)
```

## How GraphQL Works
```
flow:
  1_schema_definition:
    description: Server defines types, queries, mutations, subscriptions
    note: Schema is the contract between client and server

  2_client_sends_query:
    description: Client sends a query document specifying exact fields needed
    transport: "POST /graphql with JSON body containing query string"

  3_server_resolves:
    description: Server matches query to resolver functions
    resolvers: Each field in schema has a resolver that fetches its data

  4_server_responds:
    description: Response mirrors the shape of the query
    note: Client gets exactly what it asked for, nothing more

  single_endpoint:
    rest: "GET /users/1, GET /users/1/orders, GET /orders/5/items (3 requests)"
    graphql: "POST /graphql with nested query (1 request, exact fields)"
```

## Schema and Type System
```
type_system:
  scalar_types:
    built_in:
      - "Int - 32-bit integer"
      - "Float - double precision floating point"
      - "String - UTF-8 string"
      - "Boolean - true/false"
      - "ID - unique identifier (serialized as String)"
    custom: "scalar DateTime, scalar JSON (defined by server)"

  object_types:
    description: Core building block, defines a type with fields
    example: |
      type User {
        id: ID!
        name: String!
        email: String!
        age: Int
        posts: [Post!]!
        createdAt: DateTime!
      }

      type Post {
        id: ID!
        title: String!
        body: String!
        author: User!
        comments: [Comment!]!
      }

  modifiers:
    "String": "Nullable string"
    "String!": "Non-null string (required)"
    "[String]": "Nullable list of nullable strings"
    "[String!]!": "Non-null list of non-null strings"

  enum_types:
    example: |
      enum Role {
        ADMIN
        USER
        MODERATOR
      }

  input_types:
    description: Special types for mutation arguments
    example: |
      input CreateUserInput {
        name: String!
        email: String!
        role: Role = USER
      }

  interface_types:
    example: |
      interface Node {
        id: ID!
      }

      type User implements Node {
        id: ID!
        name: String!
      }

  union_types:
    example: |
      union SearchResult = User | Post | Comment
```

## Queries
```
queries:
  basic_query:
    description: Read data from the server
    example: |
      query {
        user(id: "42") {
          id
          name
          email
        }
      }
    response: |
      {
        "data": {
          "user": {
            "id": "42",
            "name": "Ankit",
            "email": "ankit@example.com"
          }
        }
      }

  nested_query:
    description: Fetch related data in one request
    example: |
      query {
        user(id: "42") {
          name
          posts {
            title
            comments {
              body
              author {
                name
              }
            }
          }
        }
      }

  query_with_arguments:
    example: |
      query {
        users(limit: 10, offset: 0, role: ADMIN) {
          id
          name
          role
        }
      }

  named_query_with_variables:
    description: Reusable query with variable placeholders
    query: |
      query GetUser($id: ID!) {
        user(id: $id) {
          id
          name
          email
        }
      }
    variables: |
      { "id": "42" }

  aliases:
    description: Rename fields to avoid conflicts
    example: |
      query {
        admin: user(id: "1") { name }
        viewer: user(id: "42") { name }
      }

  fragments:
    description: Reusable field selections
    example: |
      fragment UserFields on User {
        id
        name
        email
      }

      query {
        user(id: "42") { ...UserFields }
        users(limit: 5) { ...UserFields }
      }
```

## Mutations
```
mutations:
  description: Create, update, or delete data (write operations)

  create:
    example: |
      mutation {
        createUser(input: { name: "Ankit", email: "ankit@example.com" }) {
          id
          name
          email
        }
      }

  update:
    example: |
      mutation {
        updateUser(id: "42", input: { name: "Ankit Kumar" }) {
          id
          name
        }
      }

  delete:
    example: |
      mutation {
        deleteUser(id: "42") {
          success
          message
        }
      }

  with_variables:
    query: |
      mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) {
          id
          name
        }
      }
    variables: |
      {
        "input": {
          "name": "Ankit",
          "email": "ankit@example.com"
        }
      }
```

## Subscriptions
```
subscriptions:
  description: Real-time updates pushed from server to client
  transport: WebSocket (graphql-ws protocol)

  example:
    subscription: |
      subscription {
        messageAdded(chatId: "room-1") {
          id
          body
          author {
            name
          }
          createdAt
        }
      }
    flow:
      - Client opens WebSocket connection to /graphql
      - Client sends subscription query
      - Server pushes data whenever event occurs
      - Client receives updates in real-time
```

## Resolvers
```
resolvers:
  description: Functions that populate each field in the schema
  signature: "resolver(parent, args, context, info)"

  parameters:
    parent: "Result from the parent resolver (for nested fields)"
    args: "Arguments passed to the field"
    context: "Shared context (auth, DB connection, dataloaders)"
    info: "Query AST and schema info"

  example:
    schema: |
      type Query {
        user(id: ID!): User
        users(limit: Int): [User!]!
      }

      type User {
        id: ID!
        name: String!
        posts: [Post!]!
      }
    resolvers: |
      Query: {
        user: (_, { id }, { db }) => db.users.findById(id),
        users: (_, { limit }, { db }) => db.users.findAll({ limit }),
      }
      User: {
        posts: (parent, _, { db }) => db.posts.findByUserId(parent.id),
      }
```

## N+1 Problem and DataLoader
```
n_plus_1_problem:
  description: When resolving a list, each item triggers a separate DB query
  example:
    query: |
      query {
        users(limit: 10) {
          name
          posts { title }
        }
      }
    problem:
      - "1 query: SELECT * FROM users LIMIT 10"
      - "10 queries: SELECT * FROM posts WHERE user_id = ? (once per user)"
      - "Total: 11 queries instead of 2"

  solution_dataloader:
    description: Batches and caches individual loads within a single request
    how_it_works:
      - Collects all IDs requested in current tick
      - Executes one batched query for all IDs
      - Distributes results back to individual resolvers
    result:
      - "1 query: SELECT * FROM users LIMIT 10"
      - "1 query: SELECT * FROM posts WHERE user_id IN (1,2,3,...,10)"
      - "Total: 2 queries"

    implementation: |
      const DataLoader = require('dataloader');

      const postLoader = new DataLoader(async (userIds) => {
        const posts = await db.posts.findByUserIds(userIds);
        // Return posts grouped by userId in same order as input
        return userIds.map(id => posts.filter(p => p.userId === id));
      });

      // In resolver
      User: {
        posts: (parent) => postLoader.load(parent.id)
      }
```

## GraphQL vs REST
```
comparison:
  data_fetching:
    rest: "Multiple endpoints, fixed response shape, over/under-fetching"
    graphql: "Single endpoint, client chooses fields, exact data"

  endpoints:
    rest: "Many (GET /users, GET /users/:id, GET /posts)"
    graphql: "One (POST /graphql)"

  versioning:
    rest: "Version via URL (/v1/, /v2/) or headers"
    graphql: "Versionless - add new fields, deprecate old ones"

  caching:
    rest: "Easy - HTTP caching with GET requests and URLs as cache keys"
    graphql: "Harder - POST requests, need normalized client cache (Apollo)"

  error_handling:
    rest: "HTTP status codes (404, 500)"
    graphql: "Always 200, errors in response body errors array"

  file_upload:
    rest: "Easy - multipart/form-data"
    graphql: "Harder - need multipart spec extension"

  learning_curve:
    rest: "Low - uses standard HTTP"
    graphql: "Higher - schema, types, resolvers, dataloaders"

  when_to_use_graphql:
    - Multiple clients needing different data shapes (web, mobile, IoT)
    - Complex nested relationships
    - Rapid frontend iteration without backend changes
    - Aggregating data from multiple backend services

  when_to_use_rest:
    - Simple CRUD APIs
    - File upload/download heavy APIs
    - Public APIs (easier to cache and rate-limit)
    - Microservice-to-microservice communication
```

## Code Examples

### GraphQL Server in Node.js (Apollo)
```javascript
const { ApolloServer } = require("@apollo/server");
const { startStandaloneServer } = require("@apollo/server/standalone");
const DataLoader = require("dataloader");

// In-memory data store
let users = [
  { id: "1", name: "Ankit", email: "ankit@example.com" },
  { id: "2", name: "Priya", email: "priya@example.com" },
];

let posts = [
  { id: "1", title: "GraphQL Basics", body: "Learn GraphQL...", authorId: "1" },
  { id: "2", title: "Node.js Tips", body: "Useful tips...", authorId: "1" },
  { id: "3", title: "React Hooks", body: "Understanding hooks...", authorId: "2" },
];

let nextUserId = 3;
let nextPostId = 4;

// Schema
const typeDefs = `#graphql
  type User {
    id: ID!
    name: String!
    email: String!
    posts: [Post!]!
  }

  type Post {
    id: ID!
    title: String!
    body: String!
    author: User!
  }

  type Query {
    user(id: ID!): User
    users(limit: Int, offset: Int): [User!]!
    post(id: ID!): Post
  }

  input CreateUserInput {
    name: String!
    email: String!
  }

  input CreatePostInput {
    title: String!
    body: String!
    authorId: ID!
  }

  type DeleteResult {
    success: Boolean!
    message: String!
  }

  type Mutation {
    createUser(input: CreateUserInput!): User!
    createPost(input: CreatePostInput!): Post!
    deleteUser(id: ID!): DeleteResult!
  }
`;

// Resolvers
const resolvers = {
  Query: {
    user: (_, { id }) => users.find((u) => u.id === id),
    users: (_, { limit = 10, offset = 0 }) => users.slice(offset, offset + limit),
    post: (_, { id }) => posts.find((p) => p.id === id),
  },

  Mutation: {
    createUser: (_, { input }) => {
      const user = { id: String(nextUserId++), ...input };
      users.push(user);
      return user;
    },
    createPost: (_, { input }) => {
      const post = { id: String(nextPostId++), ...input };
      posts.push(post);
      return post;
    },
    deleteUser: (_, { id }) => {
      const index = users.findIndex((u) => u.id === id);
      if (index === -1) return { success: false, message: "User not found" };
      users.splice(index, 1);
      posts = posts.filter((p) => p.authorId !== id);
      return { success: true, message: "User deleted" };
    },
  },

  // Nested resolvers with DataLoader (via context)
  User: {
    posts: (parent, _, { postsByAuthorLoader }) => {
      return postsByAuthorLoader.load(parent.id);
    },
  },

  Post: {
    author: (parent, _, { userLoader }) => {
      return userLoader.load(parent.authorId);
    },
  },
};

// Server setup
async function main() {
  const server = new ApolloServer({ typeDefs, resolvers });

  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
    context: async () => ({
      // DataLoader instances are per-request (fresh for each request)
      userLoader: new DataLoader(async (ids) => {
        return ids.map((id) => users.find((u) => u.id === id));
      }),
      postsByAuthorLoader: new DataLoader(async (authorIds) => {
        return authorIds.map((authorId) =>
          posts.filter((p) => p.authorId === authorId)
        );
      }),
    }),
  });

  console.log(`GraphQL server running at ${url}`);
}

main();
```

### GraphQL Client Queries
```javascript
// Using fetch (no library needed)
async function graphqlRequest(query, variables = {}) {
  const res = await fetch("http://localhost:4000/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) {
    console.error("GraphQL errors:", json.errors);
  }
  return json.data;
}

// Query: Get user with posts
const userData = await graphqlRequest(`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      posts {
        title
        body
      }
    }
  }
`, { id: "1" });

console.log(userData.user);
// { id: "1", name: "Ankit", email: "ankit@example.com", posts: [...] }

// Query: List users (only id and name, no email - no over-fetching)
const usersData = await graphqlRequest(`
  query {
    users(limit: 10) {
      id
      name
    }
  }
`);

// Mutation: Create a user
const newUser = await graphqlRequest(`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id
      name
      email
    }
  }
`, { input: { name: "Rahul", email: "rahul@example.com" } });

console.log("Created:", newUser.createUser);

// Mutation: Delete a user
const result = await graphqlRequest(`
  mutation {
    deleteUser(id: "1") {
      success
      message
    }
  }
`);

console.log(result.deleteUser);
```
