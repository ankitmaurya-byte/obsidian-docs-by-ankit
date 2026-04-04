# Database Indexing

## What are Indexes
```
overview:
  description: |
    An index is a data structure that improves the speed of data retrieval
    at the cost of additional storage and slower writes. Without an index,
    the database must scan every row (sequential scan) to find matching data.
  analogy: |
    Like a book's index - instead of reading every page to find "B-tree",
    you look up "B-tree" in the index and go directly to page 142.
  trade_offs:
    benefits:
      - Dramatically faster SELECT/WHERE/JOIN/ORDER BY
      - Can turn O(n) sequential scan into O(log n) index lookup
    costs:
      - Extra disk space (10-30% of table size per index)
      - Slower INSERT/UPDATE/DELETE (must update index too)
      - Index maintenance and bloat over time
```

## Index Types
```
index_types:

  b_tree:
    description: Balanced tree, default index type in most databases
    structure: |
      Self-balancing tree where each node contains sorted keys.
      Leaf nodes are linked for efficient range scans.
      Typical depth: 3-4 levels for millions of rows.
    supports:
      - "Equality: WHERE id = 5"
      - "Range: WHERE age > 25"
      - "Sorting: ORDER BY created_at"
      - "Prefix matching: WHERE name LIKE 'Ank%'"
    does_not_support:
      - "Pattern matching: WHERE name LIKE '%nkit'"
    create: "CREATE INDEX idx_users_age ON users USING btree (age);"
    note: Default type, you don't need to specify USING btree

  hash:
    description: Hash table, fast equality lookups only
    supports:
      - "Equality only: WHERE id = 5"
    does_not_support:
      - Range queries
      - Sorting
      - Partial matching
    create: "CREATE INDEX idx_users_email ON users USING hash (email);"
    when_to_use: Only exact match lookups on high-cardinality columns
    note: Rarely used, B-tree handles equality almost as fast and is more flexible

  gin:
    full_name: Generalized Inverted Index
    description: Maps values to sets of rows that contain them
    supports:
      - Full-text search (tsvector)
      - JSONB containment (@>, ?, ?|, ?&)
      - Array containment (@>, &&)
      - Trigram similarity (pg_trgm)
    create_examples:
      full_text: "CREATE INDEX idx_articles_search ON articles USING gin (to_tsvector('english', title || ' ' || body));"
      jsonb: "CREATE INDEX idx_data_props ON events USING gin (metadata jsonb_path_ops);"
      array: "CREATE INDEX idx_tags ON posts USING gin (tags);"
    when_to_use: Full-text search, JSONB queries, array operations

  gist:
    full_name: Generalized Search Tree
    description: Framework for implementing custom index strategies
    supports:
      - Geometric data (PostGIS)
      - Range types (int4range, tsrange)
      - Full-text search (slower than GIN but smaller, faster updates)
      - Nearest-neighbor queries
    create_examples:
      geometry: "CREATE INDEX idx_locations ON places USING gist (geom);"
      range: "CREATE INDEX idx_booking_dates ON bookings USING gist (date_range);"
    when_to_use: Spatial data, range types, overlap queries

  brin:
    full_name: Block Range Index
    description: Stores min/max per block of table pages, very compact
    create: "CREATE INDEX idx_logs_created ON logs USING brin (created_at);"
    when_to_use: |
      Large tables where data is physically ordered (e.g., append-only logs
      where created_at increases monotonically). Tiny index size.
    note: Useless if data is randomly ordered on disk
```

## Clustered vs Non-Clustered
```
clustered_vs_non_clustered:

  clustered_index:
    description: |
      Table data is physically ordered on disk by the index column.
      Only ONE clustered index per table (because data can only be
      sorted one way physically).
    postgresql: |
      PostgreSQL does not maintain clustering automatically.
      CLUSTER command reorders once, but new inserts go to end.
      CREATE INDEX idx_orders_date ON orders(created_at);
      CLUSTER orders USING idx_orders_date;
    mysql: |
      InnoDB primary key IS the clustered index.
      Data is stored in primary key order.
    benefit: Range scans on the clustered column are extremely fast (sequential I/O)

  non_clustered_index:
    description: |
      Separate structure that points back to the table rows.
      Can have many non-clustered indexes per table.
      Most indexes you create are non-clustered.
    how_it_works: |
      Index stores: (indexed_value -> row_pointer/ctid)
      1. Look up value in index
      2. Follow pointer to heap/table to get full row
    note: Extra hop to table adds overhead compared to clustered
```

## Composite Indexes
```
composite_indexes:

  description: Index on multiple columns, column order matters

  create: "CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);"

  leftmost_prefix_rule: |
    A composite index (A, B, C) can be used for queries on:
      - A            (yes)
      - A, B         (yes)
      - A, B, C      (yes)
      - B            (no - must start from leftmost)
      - B, C         (no)
      - A, C         (partial - uses A, skips to C)

  example: |
    -- Index: (user_id, status, created_at)

    -- Uses full index
    SELECT * FROM orders WHERE user_id = 1 AND status = 'active' ORDER BY created_at;

    -- Uses first two columns
    SELECT * FROM orders WHERE user_id = 1 AND status = 'active';

    -- Uses only first column
    SELECT * FROM orders WHERE user_id = 1;

    -- Cannot use index (doesn't start with user_id)
    SELECT * FROM orders WHERE status = 'active';

  column_order_strategy: |
    1. Equality columns first (user_id = 1)
    2. Range columns next (created_at > '2025-01-01')
    3. Sort columns last (ORDER BY created_at)
```

## Covering Indexes
```
covering_indexes:

  description: |
    An index that contains ALL columns needed by a query.
    Database can answer the query from the index alone without
    touching the table (index-only scan).

  example: |
    -- Query: SELECT name, email FROM users WHERE age > 25;

    -- Regular index (needs table lookup for name, email)
    CREATE INDEX idx_age ON users(age);

    -- Covering index (answers entire query from index)
    CREATE INDEX idx_age_cover ON users(age) INCLUDE (name, email);

  include_syntax: |
    -- PostgreSQL INCLUDE (non-key columns stored in index but not searchable)
    CREATE INDEX idx_orders_user ON orders(user_id) INCLUDE (total, status);

    -- This query becomes an index-only scan:
    SELECT total, status FROM orders WHERE user_id = 1;

  benefit: |
    Index-only scans are significantly faster because:
    - No random I/O to heap/table
    - Index is smaller than table, more fits in memory
    - Fewer pages to read from disk
```

## Partial Indexes
```
partial_indexes:

  description: Index only a subset of rows matching a WHERE condition

  examples:
    active_users: |
      -- Only index active users (skip millions of inactive)
      CREATE INDEX idx_active_users ON users(email) WHERE active = true;

      -- This query uses the partial index:
      SELECT * FROM users WHERE active = true AND email = 'ankit@example.com';

    recent_orders: |
      -- Only index recent orders
      CREATE INDEX idx_recent_orders ON orders(user_id, created_at)
      WHERE created_at > '2025-01-01';

    non_null: |
      -- Only index rows where column is not null
      CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;

  benefits:
    - Smaller index size (less disk, more fits in memory)
    - Faster index maintenance (fewer rows to update)
    - More targeted, better performance for specific queries

  requirement: Query WHERE clause must match or be a subset of the index WHERE clause
```

## Index Scan vs Sequential Scan
```
scan_types:

  sequential_scan:
    description: Read every row in the table from start to end
    when_used:
      - No suitable index exists
      - Query returns large percentage of table (>5-10%)
      - Table is very small (index overhead not worth it)
      - Database estimates seq scan is faster
    cost: O(n) - reads all pages

  index_scan:
    description: Look up value in index, then fetch matching rows from table
    when_used:
      - Suitable index exists
      - Query is selective (returns small percentage of rows)
    cost: O(log n) lookup + random I/O to table for each row

  index_only_scan:
    description: All needed data is in the index, no table access
    when_used:
      - Covering index contains all columns in SELECT and WHERE
      - Visibility map confirms rows are all-visible
    cost: O(log n) lookup, no table access

  bitmap_index_scan:
    description: Scan index to build bitmap of matching pages, then read pages
    when_used:
      - Multiple indexes combined with AND/OR
      - Medium selectivity (too many rows for index scan, too few for seq scan)
    how_it_works: |
      1. Scan index A -> bitmap of matching pages
      2. Scan index B -> bitmap of matching pages
      3. AND/OR the bitmaps together
      4. Fetch matching pages from table

  planner_decision: |
    The query planner estimates cost of each strategy and picks cheapest.
    Factors: table size, index size, row selectivity, correlation,
    available memory, random_page_cost vs seq_page_cost settings.
```

## EXPLAIN ANALYZE
```
explain_analyze:

  basic_explain:
    command: "EXPLAIN SELECT * FROM users WHERE email = 'ankit@example.com';"
    description: Shows the query plan WITHOUT executing the query
    output: |
      Index Scan using idx_users_email on users  (cost=0.42..8.44 rows=1 width=72)
        Index Cond: (email = 'ankit@example.com'::text)

  explain_analyze:
    command: "EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'ankit@example.com';"
    description: Actually executes the query and shows real timing
    output: |
      Index Scan using idx_users_email on users  (cost=0.42..8.44 rows=1 width=72) (actual time=0.028..0.029 rows=1 loops=1)
        Index Cond: (email = 'ankit@example.com'::text)
      Planning Time: 0.085 ms
      Execution Time: 0.052 ms

  explain_verbose:
    command: "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT * FROM users WHERE age > 25;"
    description: Shows buffer usage (cache hits vs disk reads)
    output: |
      Seq Scan on users  (cost=0.00..1693.00 rows=50000 width=72) (actual time=0.021..12.345 rows=48521 loops=1)
        Filter: (age > 25)
        Rows Removed by Filter: 51479
        Buffers: shared hit=443
      Planning Time: 0.065 ms
      Execution Time: 15.123 ms

  reading_explain_output:
    cost: "estimated_startup_cost..total_cost (arbitrary units)"
    rows: "estimated number of rows returned"
    actual_time: "real time in milliseconds (startup..total)"
    loops: "how many times this node was executed"
    buffers_shared_hit: "pages found in cache (good)"
    buffers_shared_read: "pages read from disk (slow)"

  what_to_look_for:
    - "Seq Scan on large tables - missing index?"
    - "Rows Removed by Filter is high - index not selective enough"
    - "Nested Loop with high loops count - consider JOIN strategy"
    - "Sort with external merge - increase work_mem"
    - "Estimated rows vs actual rows differ wildly - run ANALYZE"

  force_analyze: |
    -- Update table statistics so planner makes better decisions
    ANALYZE users;
    -- Or for specific columns
    ANALYZE users (email, age);
```

## PostgreSQL Index Examples
```
postgresql_examples:

  create_indexes: |
    -- B-tree (default): equality, range, sort
    CREATE INDEX idx_users_email ON users(email);
    CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

    -- Composite: multi-column queries
    CREATE INDEX idx_orders_user_status ON orders(user_id, status);

    -- Partial: subset of rows
    CREATE INDEX idx_active_users ON users(email) WHERE active = true;

    -- Covering: index-only scans
    CREATE INDEX idx_orders_user ON orders(user_id) INCLUDE (total, status);

    -- Expression: computed values
    CREATE INDEX idx_users_lower_email ON users(lower(email));

    -- GIN: full-text search
    CREATE INDEX idx_articles_fts ON articles USING gin(to_tsvector('english', body));

    -- GIN: JSONB
    CREATE INDEX idx_events_meta ON events USING gin(metadata);

    -- BRIN: time-series, append-only
    CREATE INDEX idx_logs_ts ON logs USING brin(created_at);

  concurrent_index:
    description: Create index without locking the table for writes
    command: "CREATE INDEX CONCURRENTLY idx_users_email ON users(email);"
    note: Takes longer but doesn't block INSERT/UPDATE/DELETE

  reindex:
    description: Rebuild bloated or corrupted index
    command: "REINDEX INDEX idx_users_email;"
    concurrent: "REINDEX INDEX CONCURRENTLY idx_users_email;"

  check_index_usage: |
    -- See if indexes are being used
    SELECT
      schemaname, tablename, indexname,
      idx_scan AS times_used,
      idx_tup_read AS rows_read,
      pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
    FROM pg_stat_user_indexes
    ORDER BY idx_scan DESC;

  find_unused_indexes: |
    -- Indexes that have never been scanned
    SELECT indexname, tablename,
           pg_size_pretty(pg_relation_size(indexrelid)) AS size
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0
    ORDER BY pg_relation_size(indexrelid) DESC;

  table_vs_index_size: |
    SELECT
      relname AS table_name,
      pg_size_pretty(pg_table_size(relid)) AS table_size,
      pg_size_pretty(pg_indexes_size(relid)) AS indexes_size,
      pg_size_pretty(pg_total_relation_size(relid)) AS total_size
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC;
```

## When to Index / When NOT to Index
```
indexing_decisions:

  when_to_create_index:
    - "Columns in WHERE clauses (especially equality and range filters)"
    - "Columns in JOIN conditions (foreign keys)"
    - "Columns in ORDER BY (avoid expensive sorts)"
    - "Columns in GROUP BY"
    - "High cardinality columns (email, user_id) - many unique values"
    - "Columns queried frequently in hot paths"

  when_NOT_to_index:
    - "Small tables (<1000 rows) - sequential scan is faster"
    - "Low cardinality columns (boolean, gender, status with 2-3 values)"
    - "Tables with heavy writes and few reads"
    - "Columns rarely used in WHERE/JOIN/ORDER BY"
    - "Wide columns (large text) unless using expression index"
    - "Already have too many indexes slowing down writes"

  signs_you_need_an_index:
    - "EXPLAIN shows Seq Scan on large table"
    - "Query time increases linearly with table size"
    - "High Rows Removed by Filter in EXPLAIN"
    - "Application is slow on specific queries"

  signs_of_over_indexing:
    - "INSERT/UPDATE/DELETE are slow"
    - "Index size exceeds table size"
    - "pg_stat_user_indexes shows idx_scan = 0 for many indexes"
    - "Write-heavy workload with minimal reads"
```

## Index Bloat
```
index_bloat:

  what_it_is: |
    When rows are updated or deleted, the old index entries are not
    immediately removed. Over time, indexes accumulate dead entries
    (bloat), making them larger and slower than necessary.

  causes:
    - Frequent UPDATE operations (PostgreSQL creates new version, old stays in index)
    - Bulk DELETE without VACUUM
    - Long-running transactions preventing cleanup
    - Autovacuum not running frequently enough

  detect_bloat: |
    -- Check estimated bloat ratio
    SELECT
      schemaname, tablename, indexname,
      pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
      idx_scan AS times_used
    FROM pg_stat_user_indexes
    ORDER BY pg_relation_size(indexrelid) DESC;

    -- Use pgstattuple extension for accurate bloat measurement
    CREATE EXTENSION IF NOT EXISTS pgstattuple;
    SELECT * FROM pgstatindex('idx_users_email');

  fix_bloat:
    vacuum: |
      -- Regular vacuum marks dead tuples as reusable
      VACUUM users;
      -- Full vacuum reclaims disk space (locks table)
      VACUUM FULL users;

    reindex: |
      -- Rebuild index from scratch
      REINDEX INDEX idx_users_email;
      -- Without locking writes
      REINDEX INDEX CONCURRENTLY idx_users_email;

    autovacuum_tuning: |
      -- Tune autovacuum for high-write tables
      ALTER TABLE orders SET (
        autovacuum_vacuum_threshold = 50,
        autovacuum_vacuum_scale_factor = 0.05,
        autovacuum_analyze_threshold = 50,
        autovacuum_analyze_scale_factor = 0.05
      );

  prevention:
    - "Ensure autovacuum is running and tuned properly"
    - "Avoid very long-running transactions"
    - "Monitor index size growth over time"
    - "Schedule periodic REINDEX for high-churn tables"
    - "Use fillfactor < 100 for frequently updated tables"
```

## Best Practices
```
best_practices:

  design:
    - "Start with no indexes, add based on actual slow queries"
    - "Use EXPLAIN ANALYZE before and after adding an index"
    - "Composite index column order: equality, range, sort"
    - "Prefer partial indexes when queries always filter on a condition"
    - "Use INCLUDE for covering indexes instead of adding columns to key"

  maintenance:
    - "Monitor unused indexes and drop them"
    - "Run ANALYZE after bulk data loads"
    - "Use CREATE INDEX CONCURRENTLY in production"
    - "Watch for index bloat on high-write tables"
    - "Keep index count reasonable: 5-10 per table is typical"

  common_mistakes:
    - "Indexing every column (slows writes, wastes space)"
    - "Wrong column order in composite index"
    - "Indexing low-cardinality columns (boolean, status)"
    - "Not using partial indexes when applicable"
    - "Forgetting to ANALYZE after bulk changes"
    - "Creating duplicate/overlapping indexes"
```
