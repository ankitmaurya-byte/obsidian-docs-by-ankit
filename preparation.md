# DBMS Fundamentals (Core Concepts)


- [[What is a DBMS^]]? Difference between DBMS and RDBMS? - File system, XML DB ^d9610a
	- - Stores data in structured format
    
	- Allows CRUD operations (Create, Read, Update, Delete)
	    
	- Ensures **security & access control**
	    
	- Maintains **data consistency**
	    
	- Handles **concurrent users**
	- stores data in **tables (rows & columns)** and maintains **relationships between tables**. - MySQL, PostgreSQL, Oracle
    
- What is a **schema vs instance**?
	- [[#^d9610a]] of table interface 
	- instance is actual data ? schema
	- **Schema** defines the structure of the database, while **instance** represents the actual data stored in the database at a specific moment.
    
- What are **ACID properties**? Explain with real examples.
	-  **A** → Atomicity
		    transaction should complate all either nothing
	- **C** → Consistency
		- Database must always remain in a **valid state** before and after transaction.
	    
	- **I** → Isolation
		- Multiple transactions should **not interfere** with each other.
	    
	- **D** → Durability
		- Once transaction is **committed**, it is **permanently saved** — even if system crashes.
    
- What are **keys**? (Primary, Foreign, Candidate, Super key)
    
- What is **normalization**? Why do we need it?
    
- Explain **1NF, 2NF, 3NF, BCNF** with examples.
	- Normalization organizes data into multiple related tables to eliminate redundancy and ensure data integrity, progressing from 1NF to BCNF by removing different types of dependencies.
	- normal form
		|1NF|Atomic values|Repeating groups|
		
		|2NF|No partial dependency|Partial dependency|
	
		|3NF|No transitive dependency|Indirect dependency|
		
		|BCNF|Determinant = candidate key|Advanced anomalies|
	    
- What is **denormalization**? When should you use it?
    
- Difference between **DELETE, TRUNCATE, DROP**
    
- What is **view**? Difference between view and table?
    
- What is **index**? Why is it used?

- Difference between **clustered vs non-clustered index
	- A clustered index is used when physical ordering improves performance (like range queries), while non-clustered indexes are used for fast lookups on frequently searched columns without affecting data storage.
	- A clustered index stores data in sorted order physically, whereas a non-clustered index stores pointers to the actual data in a separate structure.**
	- Data is physically stored sorted by `id`
	- A **non-clustered index** is a **separate structure** that stores:
		- You can have **multiple** non-clustered indexes
		- CREATE INDEX idx_name ON Users(name);

- Indexed column(s)
    
- Pointer to actual data
    
- What is **composite index** and when to use it?
    
- What is **deadlock**? How to prevent it?
    
- What is **locking** (shared vs exclusive)?
    
- What is **isolation level**? (Read uncommitted → Serializable)
    
- What is **phantom read / dirty read / non-repeatable read**?
    
- What is **CAP theorem**?
    
- Difference between **OLTP vs OLAP**
    
- What is **sharding vs partitioning**?



SQL Query Questions

- Find second highest salary
    
- Find duplicate records
    
- Delete duplicate records
    
- Difference between `WHERE` vs `HAVING`
    
- Difference between `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`
    
- What is `GROUP BY`?
- Find second highest salary
    
- Find duplicate records
    
- Delete duplicate records
    
- Difference between `WHERE` vs `HAVING`
    
- Difference between `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`
    
	- What is `GROUP BY`?
- - Write query to detect **gaps in time series**
    
- Find **Nth highest salary without LIMIT**
    
- Query optimization for **slow joins**
    
- Window functions vs subqueries (when and why)
    
- Recursive queries (CTE)

Query Optimization & Performance
- How does an **index improve performance**?
    
- What is **query execution plan**?
    
- What is **full table scan**?
    
- What is **covering index**?
- - How does an **index improve performance**?
    
- What is **query execution plan**?
    
- What is **full table scan**?
    
- What is **covering index**?

- Design a **User-Order system**
    
- Design **E-commerce DB schema**
    
- Design **Twitter DB schema**
    
- Design **Chat system (messages, users, groups)**

- How would you design **likes/comments system**?
    
- How to store **large logs efficiently**?
    
- How to design **audit tables**?
    
- How to handle **soft deletes vs hard deletes**?

High-Level System Design (HLD)
- Design **URL Shortener (like bit.ly)**
    
- Design **Instagram / Twitter feed**
    
- Design **YouTube system**
    
- Design **WhatsApp / Chat system**
    
- Design **E-commerce system (Amazon)**
- - Design **URL Shortener (like bit.ly)**
    
- Design **Instagram / Twitter feed**
    
- Design **YouTube system**
    
- Design **WhatsApp / Chat system**
    
- Design **E-commerce system (Amazon)**
- Why is your query slow even after indexing?
    
- Can indexing ever **slow down performance**?
    
- What happens internally when you run a query?
    
- How does database handle **concurrency**?
    
- If DB goes down → what will you do?
    
- How to design **fault-tolerant DB system**?
    
- Tradeoff between **consistency vs availability**

- Second highest salary
    
- Top 3 salaries per department
    
- Employees with no manager
    
- Find duplicate emails
    
- Find customers with no orders
    
- Running total of sales
    
- Detect overlapping intervals