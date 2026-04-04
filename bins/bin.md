High-Volume Event Logging (Webhooks)

Monthly Reporting (Twilio & WhatsApp)

3. Real-Time Analytics Dashboard

Audit Trails (OpenAI Responses)

- **Write Speed:** Webhooks can arrive in unpredictable bursts (thousands at once). DynamoDB handles this "write pressure" effortlessly because it is serverless.
- **Flexible Schema:** Webhooks often contain JSON payloads with varying structures. Since DynamoDB is NoSQL, you don't need to define columns for every field in the webhook; you just save the whole object.
- **DynamoDB** is "Serverless" (you don't choose a CPU or RAM size; you just read/write).
- **RDS (Postgres)** is usually "Provisioned" (you choose a server size, e.g., `db.t3.medium`, and pay for it to run 24/7).
- **Amazon RDS (Relational Database Service):** This is the standard way. You tell AWS, "I want a PostgreSQL database," and they set up a virtual server for you, install Postgres, and handle backups/patching. You get a connection string (host, port, user, password) just like you would with a local Postgres server.
- **Amazon Aurora:** This is AWS's high-performance, cloud-native version of PostgreSQL. It looks and acts exactly like Postgres to your code, but it scales faster and is more durable behind the scenes.

**NoSQL Workbench (Official):** AWS provides a free desktop app called "NoSQL Workbench." You can connect it to "Localhost:8000" and view your tables, items, and schema visually.

PROMETHEUS

GRAFANA

![[Pasted image 20260120172930.png]]

process manager for Node. pm2

learnings : event loop → non blocking —> asynchronous —>single threaded

event loop phases in node js —>> timer - > pending callback —> idle / prepare - > poll phase - > check phase → close pahase →> callback

super priority queue - > process.nexttick () priority queue - > promise

starvation- > never reaches to macrotask queue,

callback → web appi → callback continues

learning: intervue resume : Reduced API response time by 40% by improving database indexing and Express routes.”

create index name on table ( table ) —>> prevent In memory sort , uses index for sorting

helps in query latencty 70-80%

N+1 —→ with complete table want to add one column from another table use join for that , insted of fetching all both then table.columnfromtable2 = data

Api response 40% reduce - > P99, P95 —>> SLI, SLA, SLO —> : API availability , promise ,target

how to mesure , gatagod , newrlic custom response, res.oon( “ finish “) {

}

log — > ELK lastic search , **Logstash , kiban — >>aws sercive , file beat , mover - provessr , viewer → cloud watch grapfana,**

jan 5

RDS - **Aurora : cloud databse manager

ECS , EC2 , EKS

Database sharding for**

- More write throughput
- More concurrent users
- No single DB bottleneck