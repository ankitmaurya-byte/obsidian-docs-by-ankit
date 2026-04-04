```
postgresql_cli:

  connection:
    connect:
      command: psql -U postgres -d mydb
      description: Connect to a PostgreSQL database
      example: psql -U postgres -d mydb

    connect_with_host:
      command: psql -h localhost -U postgres -d mydb -p 5432
      description: Connect using host and port
      example: psql -h localhost -U postgres -d mydb -p 5432

    exit:
      command: \q
      description: Exit psql CLI
      example: \q

    connection_info:
      command: \conninfo
      description: Show current connection details
      example: \conninfo

  databases:
    list:
      command: \l
      description: List all databases
      example: \l

    create:
      command: CREATE DATABASE mydb;
      description: Create a new database
      example: CREATE DATABASE mydb;

    drop:
      command: DROP DATABASE mydb;
      description: Delete a database
      example: DROP DATABASE mydb;

    connect:
      command: \c mydb
      description: Switch to another database
      example: \c mydb

  roles_users:
    create_user:
      command: CREATE USER ankit WITH PASSWORD '1234';
      description: Create new user
      example: CREATE USER ankit WITH PASSWORD '1234';

    alter_user:
      command: ALTER USER ankit WITH PASSWORD 'newpass';
      description: Update user password
      example: ALTER USER ankit WITH PASSWORD 'newpass';

    drop_user:
      command: DROP USER ankit;
      description: Delete user
      example: DROP USER ankit;

    list_roles:
      command: \du
      description: List all users/roles
      example: \du

    grant_db_access:
      command: GRANT ALL PRIVILEGES ON DATABASE mydb TO ankit;
      description: Grant full access to database
      example: GRANT ALL PRIVILEGES ON DATABASE mydb TO ankit;

  tables:
    list:
      command: \dt
      description: List all tables
      example: \dt

    describe:
      command: \d users
      description: Show table structure
      example: \d users

    create:
      command: |
        CREATE TABLE users (
          id SERIAL PRIMARY KEY,
          name TEXT,
          email TEXT UNIQUE,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
      description: Create a table
      example: CREATE TABLE users (...);

    drop:
      command: DROP TABLE users;
      description: Delete table
      example: DROP TABLE users;

  crud:
    insert:
      command: INSERT INTO users (name, email) VALUES ('Ankit', 'ankit@example.com');
      description: Insert new record
      example: INSERT INTO users (name, email) VALUES ('Ankit', 'ankit@example.com');

    select:
      command: SELECT * FROM users;
      description: Retrieve all data
      example: SELECT * FROM users;

    select_where:
      command: SELECT * FROM users WHERE id = 1;
      description: Filter data
      example: SELECT * FROM users WHERE id = 1;

    update:
      command: UPDATE users SET name = 'Updated' WHERE id = 1;
      description: Update record
      example: UPDATE users SET name = 'Updated' WHERE id = 1;

    delete:
      command: DELETE FROM users WHERE id = 1;
      description: Delete record
      example: DELETE FROM users WHERE id = 1;

  filtering_sorting:
    where:
      command: SELECT * FROM users WHERE name = 'Ankit';
      description: Filter rows
      example: SELECT * FROM users WHERE name = 'Ankit';

    order_by:
      command: SELECT * FROM users ORDER BY id DESC;
      description: Sort results
      example: SELECT * FROM users ORDER BY id DESC;

    limit:
      command: SELECT * FROM users LIMIT 5;
      description: Limit number of rows
      example: SELECT * FROM users LIMIT 5;

  joins:
    inner_join:
      command: |
        SELECT * FROM orders
        JOIN users ON users.id = orders.user_id;
      description: Combine data from multiple tables
      example: SELECT * FROM orders JOIN users ON users.id = orders.user_id;

  aggregation:
    count:
      command: SELECT COUNT(*) FROM users;
      description: Count rows
      example: SELECT COUNT(*) FROM users;

    avg:
      command: SELECT AVG(id) FROM users;
      description: Average calculation
      example: SELECT AVG(id) FROM users;

    group_by:
      command: SELECT name, COUNT(*) FROM users GROUP BY name;
      description: Group data
      example: SELECT name, COUNT(*) FROM users GROUP BY name;

  indexes:
    create:
      command: CREATE INDEX idx_users_email ON users(email);
      description: Create index for faster queries
      example: CREATE INDEX idx_users_email ON users(email);

    drop:
      command: DROP INDEX idx_users_email;
      description: Remove index
      example: DROP INDEX idx_users_email;

  schema:
    list:
      command: \dn
      description: List schemas
      example: \dn

    create:
      command: CREATE SCHEMA my_schema;
      description: Create schema
      example: CREATE SCHEMA my_schema;

    set_path:
      command: SET search_path TO my_schema;
      description: Set default schema
      example: SET search_path TO my_schema;

  transactions:
    begin:
      command: BEGIN;
      description: Start transaction
      example: BEGIN;

    commit:
      command: COMMIT;
      description: Save changes
      example: COMMIT;

    rollback:
      command: ROLLBACK;
      description: Undo changes
      example: ROLLBACK;

  import_export:
    import:
      command: psql -U postgres -d mydb -f file.sql
      description: Import SQL file
      example: psql -U postgres -d mydb -f backup.sql

    export:
      command: pg_dump -U postgres mydb > backup.sql
      description: Export database
      example: pg_dump -U postgres mydb > backup.sql

  docker_usage:
    connect_container:
      command: docker compose exec postgres psql -U postgres -d mydb
      description: Open psql inside Docker container
      example: docker compose exec postgres psql -U postgres -d mydb

  help:
    list_commands:
      command: \?
      description: Show all psql meta commands
      example: \?

    sql_help:
      command: \h
      description: SQL syntax help
      example: \h SELECT
```