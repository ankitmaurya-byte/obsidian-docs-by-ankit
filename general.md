# System Design
## Queues & Messaging
### Redis
- Used for queues and workers
- Bull / BullMQ → built on Redis
### Core Concepts
- Queue → Where jobs are pushed
- Worker → Processes jobs
- Job → Unit of work
- Retry → Auto reattempt
- Backoff → Delay between retries
- Concurrency → Parallel processing
- Rate Limit → Protect APIs
### Messaging Systems
- Kafka
- SQS
- RabbitMQ
## Realtime
### Without WebRTC
User A → Server → User B
### With WebRTC
User A ↔ User B (direct connection)
## GCP Flow
Compute Engine (VM) → Cloud Run → App Engine → Cloud Shell → Cloud Build
# Databases
## PostgreSQL
### MVCC (Multi-Version Concurrency Control)
- Keeps multiple versions of same row
- Reads and writes don’t block each other
### Storage
- Tables stored as Heap (unordered)
### CTID
- Physical address of row
- Format → (block_number, tuple_index)
### Index Flow
1. Search index
2. Get CTID
3. Jump to disk page
4. Read row
### JSON vs JSONB
#### JSON
- Stored as plain text
- Parsed every read
- Slower
- No indexing
#### JSONB
- Stored as binary tree
- Parsed once on write
- Faster
- Supports GIN indexing
### Type System
- PostgreSQL is strongly typed
- '[]' → text ❌
- '[]'::jsonb → jsonb ✅
### COALESCE
- Query → COALESCE(jc.logs, '[]'::jsonb)
- jc.logs is NOT a variable
- It is the current value of logs column
### Indexing
#### B-Tree
- Default index
- Works only for exact match
- Cannot search inside arrays/json
#### GIN (Generalized Inverted Index)
- Used for arrays/json search
- Breaks data into key → row mapping
- Example:
  - user_A → rows 1,3
  - user_B → rows 1,2
  - user_C → row 2
### Performance
#### Without Index
- Sequential scan
- O(n)
- Slow (seconds)
#### With Index
- Direct lookup
- O(log n)
- Fast (milliseconds)
### Example Index
CREATE INDEX idx_default_btree ON job_roles ("teamMembers");


# Algolia search API (hidden network calls)