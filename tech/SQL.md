# SQL

## What is SQL
```
overview:
  full_name: Structured Query Language
  type: Declarative language for managing relational databases
  used_with:
    - PostgreSQL
    - MySQL
    - SQLite
    - SQL Server
    - Oracle
  key_concepts:
    - Tables (relations) with rows and columns
    - Schema defines structure, constraints enforce integrity
    - ACID transactions guarantee data consistency
    - Indexes speed up reads at cost of write overhead
    - Normalization reduces redundancy
```

## CRUD Operations
```
crud:

  SELECT:
    basic: "SELECT name, email FROM users;"
    all_columns: "SELECT * FROM users;"
    with_alias: "SELECT name AS full_name, age AS user_age FROM users;"
    distinct: "SELECT DISTINCT city FROM users;"
    where: "SELECT * FROM users WHERE age > 25 AND city = 'Delhi';"
    like: "SELECT * FROM users WHERE name LIKE 'Ank%';"
    in: "SELECT * FROM users WHERE city IN ('Delhi', 'Mumbai', 'Pune');"
    between: "SELECT * FROM orders WHERE created_at BETWEEN '2025-01-01' AND '2025-12-31';"
    is_null: "SELECT * FROM users WHERE phone IS NULL;"
    order_by: "SELECT * FROM users ORDER BY created_at DESC;"
    limit_offset: "SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;"

  INSERT:
    single: "INSERT INTO users (name, email) VALUES ('Ankit', 'ankit@example.com');"
    multiple: |
      INSERT INTO users (name, email) VALUES
        ('Ankit', 'ankit@example.com'),
        ('Priya', 'priya@example.com'),
        ('Rahul', 'rahul@example.com');
    returning: "INSERT INTO users (name, email) VALUES ('Ankit', 'ankit@example.com') RETURNING id;"
    from_select: |
      INSERT INTO archived_users (name, email)
      SELECT name, email FROM users WHERE active = false;

  UPDATE:
    basic: "UPDATE users SET name = 'Ankit Kumar' WHERE id = 1;"
    multiple_columns: "UPDATE users SET name = 'Ankit', city = 'Delhi' WHERE id = 1;"
    with_subquery: |
      UPDATE orders SET status = 'cancelled'
      WHERE user_id IN (SELECT id FROM users WHERE active = false);
    returning: "UPDATE users SET age = age + 1 WHERE id = 1 RETURNING *;"

  DELETE:
    basic: "DELETE FROM users WHERE id = 1;"
    with_condition: "DELETE FROM sessions WHERE expires_at < NOW();"
    delete_all: "DELETE FROM logs;  -- deletes all rows, logged"
    truncate: "TRUNCATE TABLE logs;  -- faster, not logged, resets sequences"
```

## JOINs
```
joins:

  inner_join:
    description: Returns only rows with matching values in both tables
    syntax: |
      SELECT u.name, o.total
      FROM users u
      INNER JOIN orders o ON u.id = o.user_id;
    note: Most common join, default when you just write JOIN

  left_join:
    description: Returns all rows from left table, NULLs for non-matching right rows
    syntax: |
      SELECT u.name, o.total
      FROM users u
      LEFT JOIN orders o ON u.id = o.user_id;
    use_case: Find users who have never placed an order (WHERE o.id IS NULL)

  right_join:
    description: Returns all rows from right table, NULLs for non-matching left rows
    syntax: |
      SELECT u.name, o.total
      FROM users u
      RIGHT JOIN orders o ON u.id = o.user_id;
    note: Rarely used, just swap table order and use LEFT JOIN

  full_outer_join:
    description: Returns all rows from both tables, NULLs where no match
    syntax: |
      SELECT u.name, o.total
      FROM users u
      FULL OUTER JOIN orders o ON u.id = o.user_id;
    use_case: Find unmatched rows on either side

  cross_join:
    description: Cartesian product, every row from A paired with every row from B
    syntax: |
      SELECT u.name, p.product_name
      FROM users u
      CROSS JOIN products p;
    warning: "N x M rows returned, use carefully"

  self_join:
    description: Join a table with itself
    syntax: |
      SELECT e.name AS employee, m.name AS manager
      FROM employees e
      LEFT JOIN employees m ON e.manager_id = m.id;
```

## GROUP BY and HAVING
```
aggregation:

  group_by:
    description: Groups rows sharing a value, used with aggregate functions
    aggregate_functions:
      - "COUNT(*) - number of rows"
      - "SUM(column) - total"
      - "AVG(column) - average"
      - "MIN(column) - smallest"
      - "MAX(column) - largest"
    example: |
      SELECT city, COUNT(*) AS user_count, AVG(age) AS avg_age
      FROM users
      GROUP BY city
      ORDER BY user_count DESC;

  having:
    description: Filters groups (WHERE filters rows, HAVING filters groups)
    example: |
      SELECT city, COUNT(*) AS user_count
      FROM users
      GROUP BY city
      HAVING COUNT(*) > 10
      ORDER BY user_count DESC;

  grouping_with_join: |
    SELECT u.name, COUNT(o.id) AS order_count, SUM(o.total) AS total_spent
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name
    HAVING SUM(o.total) > 1000;
```

## Subqueries
```
subqueries:

  in_where:
    description: Subquery as a filter condition
    example: |
      SELECT name, email
      FROM users
      WHERE id IN (
        SELECT user_id FROM orders WHERE total > 500
      );

  scalar_subquery:
    description: Returns a single value
    example: |
      SELECT name, salary,
        (SELECT AVG(salary) FROM employees) AS avg_salary
      FROM employees
      WHERE salary > (SELECT AVG(salary) FROM employees);

  correlated_subquery:
    description: References outer query, runs once per outer row
    example: |
      SELECT name, salary, department_id
      FROM employees e
      WHERE salary > (
        SELECT AVG(salary)
        FROM employees
        WHERE department_id = e.department_id
      );

  exists:
    description: Check if subquery returns any rows
    example: |
      SELECT name
      FROM users u
      WHERE EXISTS (
        SELECT 1 FROM orders o WHERE o.user_id = u.id
      );

  in_from:
    description: Subquery as a derived table
    example: |
      SELECT dept, avg_salary
      FROM (
        SELECT department_id AS dept, AVG(salary) AS avg_salary
        FROM employees
        GROUP BY department_id
      ) AS dept_avg
      WHERE avg_salary > 80000;
```

## Window Functions
```
window_functions:
  description: Perform calculations across related rows without collapsing them

  row_number:
    description: Unique sequential number within partition
    example: |
      SELECT name, department, salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
      FROM employees;
    use_case: "Get top N per group, deduplicate rows"

  rank_dense_rank:
    description: Rank with/without gaps for ties
    example: |
      SELECT name, salary,
        RANK() OVER (ORDER BY salary DESC) AS rank,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
      FROM employees;
    note: "RANK: 1,2,2,4  DENSE_RANK: 1,2,2,3"

  lag_lead:
    description: Access previous/next row values
    example: |
      SELECT date, revenue,
        LAG(revenue, 1) OVER (ORDER BY date) AS prev_day_revenue,
        LEAD(revenue, 1) OVER (ORDER BY date) AS next_day_revenue,
        revenue - LAG(revenue, 1) OVER (ORDER BY date) AS daily_change
      FROM daily_sales;
    use_case: Time series comparisons, calculate day-over-day changes

  sum_over:
    description: Running total
    example: |
      SELECT date, amount,
        SUM(amount) OVER (ORDER BY date) AS running_total,
        SUM(amount) OVER (PARTITION BY user_id ORDER BY date) AS user_running_total
      FROM transactions;

  ntile:
    description: Divide rows into N equal buckets
    example: |
      SELECT name, salary,
        NTILE(4) OVER (ORDER BY salary) AS salary_quartile
      FROM employees;
```

## CTEs (Common Table Expressions)
```
ctes:

  basic:
    description: Named temporary result set for readability
    example: |
      WITH active_users AS (
        SELECT id, name, email
        FROM users
        WHERE active = true AND last_login > NOW() - INTERVAL '30 days'
      )
      SELECT au.name, COUNT(o.id) AS order_count
      FROM active_users au
      JOIN orders o ON au.id = o.user_id
      GROUP BY au.name;

  multiple_ctes:
    description: Chain multiple CTEs together
    example: |
      WITH monthly_sales AS (
        SELECT DATE_TRUNC('month', created_at) AS month,
               SUM(total) AS revenue
        FROM orders
        GROUP BY month
      ),
      growth AS (
        SELECT month, revenue,
               LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
               ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
                     / LAG(revenue) OVER (ORDER BY month) * 100, 2) AS growth_pct
        FROM monthly_sales
      )
      SELECT * FROM growth ORDER BY month;

  recursive_cte:
    description: Self-referencing CTE for hierarchical data
    example: |
      WITH RECURSIVE org_chart AS (
        -- base case: top-level managers
        SELECT id, name, manager_id, 1 AS level
        FROM employees
        WHERE manager_id IS NULL

        UNION ALL

        -- recursive case: employees under managers
        SELECT e.id, e.name, e.manager_id, oc.level + 1
        FROM employees e
        JOIN org_chart oc ON e.manager_id = oc.id
      )
      SELECT * FROM org_chart ORDER BY level, name;
```

## Indexes
```
indexes:

  what_it_is: Data structure that speeds up row lookup at cost of extra storage and slower writes

  create_index: "CREATE INDEX idx_users_email ON users(email);"
  unique_index: "CREATE UNIQUE INDEX idx_users_email ON users(email);"
  composite_index: "CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);"
  partial_index: "CREATE INDEX idx_active_users ON users(email) WHERE active = true;"
  drop_index: "DROP INDEX idx_users_email;"

  when_to_index:
    - Columns in WHERE clauses
    - Columns in JOIN conditions
    - Columns in ORDER BY
    - High cardinality columns (many unique values)

  when_not_to_index:
    - Small tables (sequential scan is faster)
    - Columns with low cardinality (boolean, status with 2-3 values)
    - Tables with heavy INSERT/UPDATE (index maintenance overhead)
    - Columns rarely used in queries

  explain:
    basic: "EXPLAIN SELECT * FROM users WHERE email = 'ankit@example.com';"
    analyze: "EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'ankit@example.com';"
    note: "EXPLAIN shows plan, EXPLAIN ANALYZE actually runs the query and shows real timing"
```

## Transactions and ACID
```
transactions:

  acid:
    atomicity: All operations succeed or all fail, no partial commits
    consistency: DB moves from one valid state to another
    isolation: Concurrent transactions don't interfere with each other
    durability: Committed data survives crashes

  syntax: |
    BEGIN;
    UPDATE accounts SET balance = balance - 500 WHERE id = 1;
    UPDATE accounts SET balance = balance + 500 WHERE id = 2;
    COMMIT;
    -- or ROLLBACK; to undo

  savepoints: |
    BEGIN;
    INSERT INTO orders (user_id, total) VALUES (1, 100);
    SAVEPOINT order_created;
    INSERT INTO order_items (order_id, product_id) VALUES (1, 999);
    -- oops, product 999 doesn't exist
    ROLLBACK TO SAVEPOINT order_created;
    INSERT INTO order_items (order_id, product_id) VALUES (1, 1);
    COMMIT;

  isolation_levels:
    read_uncommitted:
      description: Can read uncommitted changes from other transactions
      problem: Dirty reads
      use: Almost never used in PostgreSQL

    read_committed:
      description: Only see committed data (PostgreSQL default)
      problem: Non-repeatable reads (row changes between reads)
      use: Most OLTP workloads

    repeatable_read:
      description: Snapshot of data at transaction start
      problem: Phantom reads in some DBs (not PostgreSQL)
      use: Reports that need consistent point-in-time view

    serializable:
      description: Transactions behave as if executed one by one
      problem: Slowest, may abort and retry transactions
      use: Financial transactions, critical consistency

    set_level: "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
```

## Normalization
```
normalization:

  purpose: Reduce data redundancy and avoid update anomalies

  first_normal_form_1NF:
    rules:
      - Each column holds atomic (indivisible) values
      - No repeating groups or arrays in a single column
    violation: "name='Ankit', skills='Go,JS,Python' -- comma-separated list"
    fix: Create a separate skills table with one skill per row

  second_normal_form_2NF:
    rules:
      - Must be in 1NF
      - Every non-key column depends on the entire primary key (no partial dependencies)
    violation: "Table(order_id, product_id, product_name) -- product_name depends only on product_id"
    fix: Split into Orders(order_id, product_id) and Products(product_id, product_name)

  third_normal_form_3NF:
    rules:
      - Must be in 2NF
      - No transitive dependencies (non-key column depends on another non-key column)
    violation: "Table(user_id, city, state) -- state depends on city, not user_id"
    fix: Split into Users(user_id, city_id) and Cities(city_id, city, state)

  practical_note: |
    Most production systems aim for 3NF.
    Denormalization is acceptable for read-heavy workloads (caching, analytics).
    Don't over-normalize: if data is always read together, keep it together.
```

## Practical Query Examples
```
practical_examples:

  top_n_per_group: |
    -- Top 3 highest-paid employees per department
    WITH ranked AS (
      SELECT name, department, salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
      FROM employees
    )
    SELECT * FROM ranked WHERE rn <= 3;

  find_duplicates: |
    SELECT email, COUNT(*) AS count
    FROM users
    GROUP BY email
    HAVING COUNT(*) > 1;

  running_total: |
    SELECT date, amount,
      SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
    FROM transactions;

  pivot_with_case: |
    SELECT
      user_id,
      SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
      SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
      SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
    FROM orders
    GROUP BY user_id;

  upsert_on_conflict: |
    INSERT INTO users (email, name, login_count)
    VALUES ('ankit@example.com', 'Ankit', 1)
    ON CONFLICT (email)
    DO UPDATE SET
      name = EXCLUDED.name,
      login_count = users.login_count + 1;

  delete_old_keep_latest: |
    DELETE FROM logs
    WHERE id NOT IN (
      SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
        FROM logs
      ) t WHERE rn <= 10
    );
```

## Go Database Example
```go
package main

import (
    "context"
    "database/sql"
    "fmt"
    "log"
    "time"

    _ "github.com/lib/pq"
)

type User struct {
    ID        int
    Name      string
    Email     string
    CreatedAt time.Time
}

func main() {
    connStr := "postgres://postgres:password@localhost:5432/mydb?sslmode=disable"
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    db.SetConnMaxLifetime(5 * time.Minute)

    ctx := context.Background()

    // INSERT with returning
    var id int
    err = db.QueryRowContext(ctx,
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id",
        "Ankit", "ankit@example.com",
    ).Scan(&id)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Inserted user ID: %d\n", id)

    // SELECT single row
    var user User
    err = db.QueryRowContext(ctx,
        "SELECT id, name, email, created_at FROM users WHERE id = $1", id,
    ).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("User: %+v\n", user)

    // SELECT multiple rows
    rows, err := db.QueryContext(ctx,
        "SELECT id, name, email, created_at FROM users ORDER BY id LIMIT 10",
    )
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    for rows.Next() {
        var u User
        rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt)
        fmt.Printf("  %d: %s <%s>\n", u.ID, u.Name, u.Email)
    }

    // Transaction
    tx, err := db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelSerializable})
    if err != nil {
        log.Fatal(err)
    }

    _, err = tx.ExecContext(ctx, "UPDATE accounts SET balance = balance - $1 WHERE id = $2", 500, 1)
    if err != nil {
        tx.Rollback()
        log.Fatal(err)
    }

    _, err = tx.ExecContext(ctx, "UPDATE accounts SET balance = balance + $1 WHERE id = $2", 500, 2)
    if err != nil {
        tx.Rollback()
        log.Fatal(err)
    }

    if err = tx.Commit(); err != nil {
        log.Fatal(err)
    }
    fmt.Println("Transfer complete")
}
```

## JavaScript Database Example
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'password',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// INSERT with returning
async function createUser(name, email) {
  const { rows } = await pool.query(
    'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
    [name, email]
  );
  return rows[0];
}

// SELECT with parameterized query (prevents SQL injection)
async function getUserById(id) {
  const { rows } = await pool.query(
    'SELECT id, name, email, created_at FROM users WHERE id = $1',
    [id]
  );
  return rows[0];
}

// Transaction
async function transferFunds(fromId, toId, amount) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query(
      'UPDATE accounts SET balance = balance - $1 WHERE id = $2',
      [amount, fromId]
    );
    await client.query(
      'UPDATE accounts SET balance = balance + $1 WHERE id = $2',
      [amount, toId]
    );
    await client.query('COMMIT');
    console.log('Transfer complete');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

// Batch insert with transaction
async function batchInsertUsers(users) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    for (const user of users) {
      await client.query(
        'INSERT INTO users (name, email) VALUES ($1, $2)',
        [user.name, user.email]
      );
    }
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

(async () => {
  const user = await createUser('Ankit', 'ankit@example.com');
  console.log('Created:', user);

  const fetched = await getUserById(user.id);
  console.log('Fetched:', fetched);

  await transferFunds(1, 2, 500);
  await pool.end();
})();
```

## Best Practices
```
best_practices:

  query_writing:
    - "Always use parameterized queries, never string concatenation"
    - "SELECT only the columns you need, avoid SELECT *"
    - "Use LIMIT for large result sets"
    - "Prefer EXISTS over IN for correlated subqueries"
    - "Use CTEs for readability over deeply nested subqueries"

  schema_design:
    - "Use appropriate data types (don't store numbers as text)"
    - "Add NOT NULL constraints where possible"
    - "Use foreign keys for referential integrity"
    - "Add CHECK constraints for business rules"
    - "Use SERIAL/IDENTITY or UUIDs for primary keys"

  performance:
    - "Index columns used in WHERE, JOIN, ORDER BY"
    - "Use EXPLAIN ANALYZE to understand query plans"
    - "Avoid N+1 queries, use JOINs or batch fetching"
    - "Use connection pooling (PgBouncer, built-in pool)"
    - "Partition large tables by date or range"
    - "Vacuum and analyze regularly (PostgreSQL)"
```
