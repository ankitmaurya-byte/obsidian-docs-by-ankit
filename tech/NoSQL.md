# NoSQL

## What is NoSQL
```
overview:
  full_name: Not Only SQL
  type: Non-relational databases optimized for specific data models
  key_traits:
    - Flexible schemas (schema-less or schema-on-read)
    - Horizontal scaling (sharding across nodes)
    - Optimized for specific access patterns
    - Trade consistency for availability and partition tolerance
  when_to_use:
    - Rapidly evolving schemas
    - Large-scale data with high write throughput
    - Hierarchical or nested data (documents)
    - Simple key-based lookups at extreme speed
    - Graph relationships (social networks, recommendations)
  when_not_to_use:
    - Complex multi-table JOINs required
    - Strong ACID guarantees needed across operations
    - Mature reporting/analytics (SQL is better)
    - Small datasets with structured relationships
```

## Types of NoSQL Databases
```
types:

  document_store:
    description: Store data as JSON/BSON documents, flexible nested structures
    examples:
      - MongoDB
      - CouchDB
      - Amazon DocumentDB
    data_model: |
      {
        "_id": "user_123",
        "name": "Ankit",
        "email": "ankit@example.com",
        "address": {
          "city": "Delhi",
          "state": "Delhi"
        },
        "orders": [
          { "id": 1, "total": 500, "status": "delivered" }
        ]
      }
    best_for: Content management, user profiles, catalogs, event logging

  key_value_store:
    description: Simple key-to-value mapping, fastest reads/writes
    examples:
      - Redis
      - Amazon DynamoDB
      - Memcached
      - etcd
    data_model: |
      key: "session:abc123"
      value: "{\"user_id\": 1, \"expires\": \"2025-12-31\"}"
    best_for: Caching, sessions, feature flags, real-time counters

  column_family:
    description: Data stored in columns instead of rows, optimized for aggregations
    examples:
      - Apache Cassandra
      - HBase
      - ScyllaDB
    data_model: |
      Row Key: "user_123"
      Column Family "profile": { name: "Ankit", email: "ankit@example.com" }
      Column Family "activity": { last_login: "2025-06-15", login_count: 42 }
    best_for: Time-series data, IoT sensor data, write-heavy workloads, analytics

  graph_database:
    description: Nodes and edges represent entities and relationships
    examples:
      - Neo4j
      - Amazon Neptune
      - ArangoDB
    data_model: |
      (Ankit)-[:FOLLOWS]->(Priya)
      (Ankit)-[:WORKS_AT]->(Company)
      (Priya)-[:LIKES]->(Post)
    best_for: Social networks, recommendation engines, fraud detection, knowledge graphs
```

## CAP Theorem
```
cap_theorem:

  description: |
    In a distributed system, you can only guarantee 2 out of 3:
    - Consistency: Every read gets the most recent write
    - Availability: Every request gets a response (even if stale)
    - Partition Tolerance: System works despite network failures

  note: |
    Network partitions WILL happen in distributed systems,
    so the real choice is between Consistency and Availability.

  database_choices:
    CP_systems:
      description: Choose consistency over availability during partition
      examples:
        - MongoDB (with majority write concern)
        - HBase
        - etcd
        - Zookeeper
      behavior: Rejects writes if can't guarantee consistency

    AP_systems:
      description: Choose availability over consistency during partition
      examples:
        - Cassandra
        - CouchDB
        - DynamoDB (default)
        - Riak
      behavior: Accepts writes, resolves conflicts later (eventual consistency)

    CA_systems:
      description: Not really possible in distributed systems
      examples:
        - Single-node PostgreSQL
        - Single-node MySQL
      note: Only works if there's no network partition (single node)
```

## BASE vs ACID
```
base_vs_acid:

  acid:
    stands_for:
      A: Atomicity - all or nothing
      C: Consistency - valid state to valid state
      I: Isolation - transactions don't interfere
      D: Durability - committed data survives crashes
    used_by: PostgreSQL, MySQL, SQL Server, Oracle
    trade_off: Stronger guarantees but harder to scale horizontally

  base:
    stands_for:
      BA: Basically Available - system guarantees availability
      S: Soft state - state may change over time without input
      E: Eventual consistency - system will become consistent eventually
    used_by: Cassandra, DynamoDB, CouchDB
    trade_off: Weaker guarantees but easier to scale horizontally

  comparison:
    consistency: "ACID = immediate | BASE = eventual"
    availability: "ACID = may block | BASE = always responds"
    scaling: "ACID = vertical (bigger machine) | BASE = horizontal (more machines)"
    use_case: "ACID = banking, orders | BASE = social feeds, analytics, caching"
```

## SQL vs NoSQL Decision Guide
```
sql_vs_nosql:

  choose_sql_when:
    - Data has clear relationships and structure
    - Need complex JOINs and aggregations
    - ACID transactions are critical (banking, e-commerce orders)
    - Schema is well-defined and stable
    - Team knows SQL and tooling is mature
    - Reporting and analytics needed

  choose_nosql_when:
    - Schema changes frequently or varies per record
    - Massive scale with high write throughput
    - Data is naturally hierarchical (nested JSON)
    - Simple access patterns (key lookup, document fetch)
    - Geographic distribution needed
    - Real-time data with eventual consistency acceptable

  common_combo: |
    Many production systems use BOTH:
    - PostgreSQL for core transactional data (users, orders, payments)
    - Redis for caching, sessions, rate limiting
    - MongoDB for content, logs, flexible schemas
    - Elasticsearch for full-text search
```

## MongoDB CRUD Examples
```
mongodb_crud:

  connect: "mongosh 'mongodb://localhost:27017/mydb'"

  create:
    insert_one: |
      db.users.insertOne({
        name: "Ankit",
        email: "ankit@example.com",
        age: 25,
        address: { city: "Delhi", state: "Delhi" },
        tags: ["developer", "golang"]
      })

    insert_many: |
      db.users.insertMany([
        { name: "Priya", email: "priya@example.com", age: 28 },
        { name: "Rahul", email: "rahul@example.com", age: 30 }
      ])

  read:
    find_all: "db.users.find()"
    find_one: "db.users.findOne({ email: 'ankit@example.com' })"
    with_filter: "db.users.find({ age: { $gt: 25 } })"
    projection: "db.users.find({}, { name: 1, email: 1, _id: 0 })"
    sort_limit: "db.users.find().sort({ age: -1 }).limit(5)"
    nested_field: "db.users.find({ 'address.city': 'Delhi' })"
    in_array: "db.users.find({ tags: { $in: ['golang', 'python'] } })"
    regex: "db.users.find({ name: { $regex: /^Ank/i } })"

  update:
    update_one: |
      db.users.updateOne(
        { email: "ankit@example.com" },
        { $set: { age: 26, "address.city": "Mumbai" } }
      )

    update_many: |
      db.users.updateMany(
        { age: { $lt: 20 } },
        { $set: { status: "junior" } }
      )

    push_to_array: |
      db.users.updateOne(
        { email: "ankit@example.com" },
        { $push: { tags: "docker" } }
      )

    increment: |
      db.users.updateOne(
        { email: "ankit@example.com" },
        { $inc: { login_count: 1 } }
      )

    upsert: |
      db.users.updateOne(
        { email: "new@example.com" },
        { $set: { name: "New User", age: 22 } },
        { upsert: true }
      )

  delete:
    delete_one: "db.users.deleteOne({ email: 'ankit@example.com' })"
    delete_many: "db.users.deleteMany({ age: { $lt: 18 } })"
    drop_collection: "db.users.drop()"

  aggregation_pipeline: |
    db.orders.aggregate([
      { $match: { status: "delivered" } },
      { $group: {
          _id: "$user_id",
          total_spent: { $sum: "$total" },
          order_count: { $sum: 1 }
      }},
      { $sort: { total_spent: -1 } },
      { $limit: 10 }
    ])

  indexes:
    create: "db.users.createIndex({ email: 1 }, { unique: true })"
    compound: "db.users.createIndex({ city: 1, age: -1 })"
    text: "db.articles.createIndex({ title: 'text', body: 'text' })"
    list: "db.users.getIndexes()"
    drop: "db.users.dropIndex('email_1')"
```

## Data Modeling - Embedding vs Referencing
```
data_modeling:

  embedding:
    description: Nest related data inside the parent document
    example: |
      // User with embedded addresses
      {
        "_id": "user_1",
        "name": "Ankit",
        "addresses": [
          { "type": "home", "city": "Delhi", "zip": "110001" },
          { "type": "work", "city": "Gurgaon", "zip": "122001" }
        ]
      }
    when_to_use:
      - Data is always read together
      - One-to-few relationship (user has 2-3 addresses)
      - Child data doesn't make sense without parent
      - Need atomic updates on the whole document
    pros:
      - Single read to get everything
      - No JOINs needed
      - Atomic writes on single document
    cons:
      - Document size limit (16MB in MongoDB)
      - Duplicated data if shared across documents
      - Hard to query embedded data independently

  referencing:
    description: Store related data in separate collections with IDs
    example: |
      // User document
      { "_id": "user_1", "name": "Ankit" }

      // Order documents
      { "_id": "order_1", "user_id": "user_1", "total": 500 }
      { "_id": "order_2", "user_id": "user_1", "total": 300 }
    when_to_use:
      - One-to-many or many-to-many relationships
      - Related data is large or grows unbounded
      - Need to query related data independently
      - Data is shared across multiple documents
    pros:
      - No document size issues
      - No data duplication
      - Easier independent queries
    cons:
      - Multiple queries needed (application-level JOINs)
      - No atomic update across collections (without transactions)

  rule_of_thumb: |
    Embed when: data is read together, 1:few, small/bounded
    Reference when: data is read separately, 1:many, large/unbounded
    Hybrid: embed summary data, reference full details
```

## Sharding and Replication
```
sharding_and_replication:

  sharding:
    description: Split data across multiple servers (horizontal partitioning)
    how_it_works: |
      - Choose a shard key (e.g., user_id, region)
      - Data is distributed across shards based on key
      - Each shard holds a subset of the total data
      - Router/proxy directs queries to correct shard
    shard_key_strategies:
      hashed: "Even distribution, no range queries on shard key"
      ranged: "Good for range queries, risk of hot spots"
      zone_based: "Route data by region/tenant"
    good_shard_key:
      - High cardinality (many unique values)
      - Even distribution of writes
      - Frequently used in queries
    bad_shard_key:
      - Low cardinality (status, boolean)
      - Monotonically increasing (timestamps create hot shard)

  replication:
    description: Copy data across multiple servers for fault tolerance and read scaling
    strategies:
      primary_secondary:
        description: One primary handles writes, secondaries replicate and serve reads
        used_by: MongoDB, PostgreSQL, MySQL
        trade_off: Read scaling easy, write scaling limited to primary
      multi_primary:
        description: Multiple nodes accept writes
        used_by: Cassandra, CouchDB, DynamoDB
        trade_off: Better write scaling, conflict resolution needed
    replication_factor: |
      Number of copies of each piece of data.
      RF=3 means 3 copies across 3 nodes.
      Handles up to RF-1 node failures.

  mongodb_example:
    replica_set: |
      // Initialize a 3-node replica set
      rs.initiate({
        _id: "myReplicaSet",
        members: [
          { _id: 0, host: "mongo1:27017" },
          { _id: 1, host: "mongo2:27017" },
          { _id: 2, host: "mongo3:27017" }
        ]
      })
    sharded_cluster: |
      // Enable sharding on database
      sh.enableSharding("mydb")
      // Shard collection by user_id (hashed)
      sh.shardCollection("mydb.orders", { user_id: "hashed" })
```

## Go MongoDB Example
```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

type User struct {
    Name    string   `bson:"name"`
    Email   string   `bson:"email"`
    Age     int      `bson:"age"`
    Tags    []string `bson:"tags"`
    Address Address  `bson:"address"`
}

type Address struct {
    City  string `bson:"city"`
    State string `bson:"state"`
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    client, err := mongo.Connect(ctx, options.Client().ApplyURI("mongodb://localhost:27017"))
    if err != nil {
        log.Fatal(err)
    }
    defer client.Disconnect(ctx)

    coll := client.Database("mydb").Collection("users")

    // Insert
    user := User{
        Name:    "Ankit",
        Email:   "ankit@example.com",
        Age:     25,
        Tags:    []string{"golang", "docker"},
        Address: Address{City: "Delhi", State: "Delhi"},
    }
    result, err := coll.InsertOne(ctx, user)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Inserted ID: %v\n", result.InsertedID)

    // Find one
    var found User
    err = coll.FindOne(ctx, bson.M{"email": "ankit@example.com"}).Decode(&found)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Found: %+v\n", found)

    // Find many with filter
    cursor, err := coll.Find(ctx, bson.M{"age": bson.M{"$gte": 20}},
        options.Find().SetSort(bson.D{{Key: "age", Value: -1}}).SetLimit(10))
    if err != nil {
        log.Fatal(err)
    }
    defer cursor.Close(ctx)

    var users []User
    cursor.All(ctx, &users)
    for _, u := range users {
        fmt.Printf("  %s (%d)\n", u.Name, u.Age)
    }

    // Update
    _, err = coll.UpdateOne(ctx,
        bson.M{"email": "ankit@example.com"},
        bson.M{
            "$set": bson.M{"age": 26},
            "$push": bson.M{"tags": "kubernetes"},
        },
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Updated")

    // Aggregation pipeline
    pipeline := mongo.Pipeline{
        {{Key: "$match", Value: bson.M{"age": bson.M{"$gte": 20}}}},
        {{Key: "$group", Value: bson.M{
            "_id":       "$address.city",
            "avg_age":   bson.M{"$avg": "$age"},
            "count":     bson.M{"$sum": 1},
        }}},
        {{Key: "$sort", Value: bson.M{"count": -1}}},
    }
    aggCursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        log.Fatal(err)
    }
    defer aggCursor.Close(ctx)

    var results []bson.M
    aggCursor.All(ctx, &results)
    for _, r := range results {
        fmt.Printf("City: %v, Avg Age: %v, Count: %v\n", r["_id"], r["avg_age"], r["count"])
    }

    // Delete
    _, err = coll.DeleteOne(ctx, bson.M{"email": "ankit@example.com"})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Deleted")
}
```

## JavaScript MongoDB Example
```javascript
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function main() {
  await client.connect();
  const db = client.db('mydb');
  const users = db.collection('users');

  // Insert
  const result = await users.insertOne({
    name: 'Ankit',
    email: 'ankit@example.com',
    age: 25,
    tags: ['golang', 'docker'],
    address: { city: 'Delhi', state: 'Delhi' },
  });
  console.log('Inserted:', result.insertedId);

  // Find
  const user = await users.findOne({ email: 'ankit@example.com' });
  console.log('Found:', user);

  // Find many
  const allUsers = await users
    .find({ age: { $gte: 20 } })
    .sort({ age: -1 })
    .limit(10)
    .toArray();
  console.log('Users:', allUsers);

  // Update
  await users.updateOne(
    { email: 'ankit@example.com' },
    {
      $set: { age: 26 },
      $push: { tags: 'kubernetes' },
    }
  );
  console.log('Updated');

  // Aggregation
  const stats = await users
    .aggregate([
      { $match: { age: { $gte: 20 } } },
      {
        $group: {
          _id: '$address.city',
          avgAge: { $avg: '$age' },
          count: { $sum: 1 },
        },
      },
      { $sort: { count: -1 } },
    ])
    .toArray();
  console.log('Stats:', stats);

  // Delete
  await users.deleteOne({ email: 'ankit@example.com' });
  console.log('Deleted');

  await client.close();
}

main().catch(console.error);
```

## Best Practices
```
best_practices:

  data_modeling:
    - "Design schema based on query patterns, not relationships"
    - "Embed data that is read together"
    - "Reference data that is large, shared, or queried independently"
    - "Denormalize for read performance, accept write overhead"

  performance:
    - "Index fields used in queries, sorts, and aggregation $match stages"
    - "Use projection to return only needed fields"
    - "Avoid unbounded arrays in documents"
    - "Use covered queries (index contains all needed fields)"
    - "Monitor slow queries with profiler"

  scaling:
    - "Choose shard key carefully, it cannot be changed easily"
    - "Use replication for read scaling and fault tolerance"
    - "Set appropriate read/write concern for your consistency needs"
    - "Plan capacity: know your data size, growth rate, and query patterns"

  general:
    - "Use schema validation in MongoDB for data integrity"
    - "Don't treat NoSQL as 'no schema', treat it as 'flexible schema'"
    - "Use transactions in MongoDB when multi-document atomicity is needed"
    - "Backup regularly: mongodump/mongorestore or cloud snapshots"
```
