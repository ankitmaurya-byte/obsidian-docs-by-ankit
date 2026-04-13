---
project: Novelty - AI Project Assistant
type: fullstack-api
language: python 3.12+
framework: FastAPI
database: Supabase (PostgreSQL)
ai_providers:
  - name: Claude (Anthropic)
    purpose: Chat, tool use, memory, background agent
    model: claude-sonnet-4-20250514
  - name: Gemini (Google)
    purpose: Image analysis / vision
    model: gemini-2.0-flash
  - name: Stability AI
    purpose: Image generation (optional, has mock fallback)
server: uvicorn
package_manager: pip
entry_point: app/main.py
run_command: uvicorn app.main:app --reload
docs_url: http://localhost:8000/docs
---
 
# Novelty — Complete Project Context

Everything you need to understand this project, explained from scratch.

---

## 1. Python Concepts Used

### `__init__.py` — What is it?

Every folder that has `__init__.py` is a **Python package** (a folder you can import from).

```
app/
├── __init__.py          ← makes "app" importable
├── routers/
│   ├── __init__.py      ← makes "app.routers" importable
│   └── chat.py
└── services/
    ├── __init__.py      ← makes "app.services" importable
    └── chat_service.py
```

Without `__init__.py`, Python won't recognize the folder as a package, and
`from app.services.chat_service import chat` would fail.

Our `__init__.py` files are **empty** — they just mark the folder as a package.
They CAN contain code, but we don't need that here.

### `from X import Y`

```python
from app.database import supabase       # import the supabase client object from app/database.py
from app.models import ProjectCreate    # import a specific class from app/models.py
from app.services.chat_service import chat  # import the chat function
```

### Type Hints

```python
def chat(project_id: str, message: str, conversation_id: str | None = None) -> dict:
```

- `project_id: str` — this parameter should be a string
- `str | None = None` — can be string OR None, defaults to None
- `-> dict` — the function returns a dictionary
- These are **hints only** — Python doesn't enforce them, but editors use them for autocomplete

### `list[str]`, `dict`, `Optional`

```python
goals: list[str]           # a list of strings, e.g. ["goal1", "goal2"]
metadata: dict             # a dictionary, e.g. {"key": "value"}
title: str | None = None   # same as Optional[str], means it can be None
```

---

## 2. FastAPI — The Web Framework

### What is FastAPI?

FastAPI is a Python web framework for building APIs. It's like Express.js for Node
or Spring Boot for Java. You define endpoints, it handles HTTP requests/responses.

### Core Concepts

#### App Instance

```python
# app/main.py
from fastapi import FastAPI
app = FastAPI(title="Novelty")   # creates the application
```

This `app` object IS the server. Everything attaches to it.

#### Routes / Endpoints

```python
@app.get("/")               # GET http://localhost:8000/
def root():
    return {"status": "ok"}  # automatically becomes JSON response
```

The `@app.get("/")` is a **decorator** — it registers the function below it
as the handler for GET requests to "/".

#### HTTP Methods

```python
@router.get("/")        # READ — list items
@router.post("/")       # CREATE — make new item
@router.patch("/{id}")  # UPDATE — modify existing item
@router.delete("/{id}") # DELETE — remove item
```

#### Path Parameters

```python
@router.get("/{project_id}")
def get_project(project_id: str):   # FastAPI extracts "project_id" from the URL
    ...
```

`GET /api/projects/abc-123` → `project_id = "abc-123"`

#### Request Body (JSON)

```python
@router.post("/")
def create_project(body: ProjectCreate):  # FastAPI parses JSON body into this model
    ...
```

Client sends: `{"name": "My Project", "description": "..."}`
FastAPI auto-validates it against `ProjectCreate` and gives you a Python object.

#### Query Parameters

```python
@router.get("/{project_id}")
def list_memories(project_id: str, category: str | None = None):
    ...
```

`GET /api/memory/abc-123?category=goal` → `category = "goal"`

#### Response Model

```python
@router.get("/", response_model=list[ProjectOut])
```

This tells FastAPI: "the response will be a list of ProjectOut objects" — it
validates the output and generates docs automatically.

#### Status Codes

```python
@router.post("/", status_code=201)   # 201 = Created
@router.post("/organize", status_code=202)  # 202 = Accepted (for async work)
@router.delete("/{id}", status_code=204)    # 204 = No Content
```

#### HTTPException

```python
from fastapi import HTTPException
raise HTTPException(404, "Project not found")  # returns {"detail": "Project not found"} with 404 status
```

### Routers — Splitting the App

Instead of putting everything in `main.py`, we split by feature:

```python
# app/routers/projects.py
router = APIRouter()

@router.get("/")
def list_projects(): ...
```

```python
# app/main.py
from app.routers import projects
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
```

Now all routes in `projects.py` are prefixed with `/api/projects`.
So `@router.get("/")` becomes `GET /api/projects/`.

---

## 3. Pydantic — Data Validation

### What is Pydantic?

Pydantic defines **data shapes** (schemas). FastAPI uses it to:
- Validate incoming JSON request bodies
- Serialize outgoing responses
- Generate API documentation

### How It Works

```python
class ProjectCreate(BaseModel):   # BaseModel = Pydantic base class
    name: str                      # required string
    description: str | None = None # optional string, defaults to None
    status: str = "active"         # optional with default value
```

If someone sends `{"name": 123}`, Pydantic will **coerce** it to `"123"`.
If someone sends `{}` (missing name), FastAPI returns a 422 validation error.

### model_dump()

```python
body = ProjectCreate(name="My App")
body.model_dump()  # → {"name": "My App", "description": None, "status": "active"}
```

Converts the Pydantic object to a plain dictionary (for inserting into DB).

---

## 4. Uvicorn — The Server

### What is Uvicorn?

Uvicorn is an **ASGI server** — it runs your FastAPI app and handles HTTP connections.
Think of it as the actual server process (like `node server.js` for Node).

```bash
uvicorn app.main:app --reload
```

Breaking this down:
- `app.main` → the Python module path: `app/main.py`
- `:app` → the variable name inside that file (our FastAPI instance)
- `--reload` → auto-restart when code changes (dev mode only)

### What Happens When You Run It

```
1. Uvicorn starts → imports app/main.py
2. main.py creates FastAPI() and registers routers
3. Uvicorn listens on http://localhost:8000
4. Request comes in → FastAPI routes it → your function runs → response sent
```

---

## 5. Supabase — The Database

### What is Supabase?

Supabase is a hosted PostgreSQL database with a REST API and Python client.
Instead of writing raw SQL queries in your app, you use their client library.

### Client Setup

```python
# app/database.py
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

This creates a single client object used everywhere.

### CRUD Operations

```python
# INSERT
supabase.table("projects").insert({"name": "My App"}).execute()

# SELECT all
supabase.table("projects").select("*").execute()

# SELECT with filter
supabase.table("projects").select("*").eq("id", project_id).execute()

# UPDATE
supabase.table("projects").update({"name": "New Name"}).eq("id", project_id).execute()

# DELETE
supabase.table("projects").delete().eq("id", project_id).execute()

# UPSERT (insert or update if exists)
supabase.table("project_memory").upsert(data, on_conflict="project_id,category,key").execute()
```

### .execute()

Every query chain ends with `.execute()` — this actually sends the request to Supabase.
The result has `.data` (list of rows) and `.count`.

### schema.sql

The `schema.sql` file defines all tables. You run it once in Supabase's SQL Editor
(Dashboard → SQL Editor → paste → Run). It creates:

| Table | Purpose |
|-------|---------|
| `projects` | Project name, description, status |
| `project_briefs` | Detailed brief per project (goals, audience, links, etc.) |
| `conversations` | Chat conversations, linked to a project |
| `messages` | Individual messages in a conversation |
| `images` | Generated images linked to projects |
| `project_memory` | Knowledge store — categorized key-value entries per project |
| `agent_jobs` | Background agent job tracking (status, result, errors) |

---

## 6. Claude API — Chat with Tools

### Basic Call

```python
import anthropic
client = anthropic.Anthropic(api_key="sk-ant-...")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system="You are a helpful assistant.",  # system prompt (instructions)
    messages=[                               # conversation history
        {"role": "user", "content": "Hello"},
    ],
)
```

### Tool Use (Function Calling)

Tools let Claude **call functions** in your code. The flow:

```
1. You define tools (name, description, input schema)
2. You send a message with tools available
3. Claude decides to use a tool → returns stop_reason="tool_use"
4. Your code executes the tool and sends the result back
5. Claude uses the result to form its final answer
6. Repeat if Claude wants more tools (loop)
```

#### Tool Definition

```python
{
    "name": "save_memory",
    "description": "Save knowledge to project memory",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {"type": "string"},
            "key": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["category", "key", "content"],
    },
}
```

#### The Tool Loop (chat_service.py)

```
User sends message
    ↓
Claude responds with tool_use block
    ↓
We execute the tool (e.g., save to DB)
    ↓
We send tool_result back to Claude
    ↓
Claude responds with text (or more tool calls)
    ↓
Final text response saved and returned
```

This loop runs up to 5 times to prevent infinite tool calling.

### Our 5 Tools

| Tool | What It Does |
|------|-------------|
| `save_memory` | Stores a fact/decision/goal in project memory DB |
| `search_memory` | Searches memory by keyword |
| `get_memory_by_category` | Gets all memories in a category (e.g., "goal") |
| `generate_image` | Creates an image from a text prompt |
| `analyze_image` | Sends an image to Gemini for analysis |

---

## 7. Gemini API — Image Analysis

Used for **vision** — analyzing images. When a user asks Claude to analyze an image:

```
Claude calls analyze_image tool
    ↓
Our code loads the image from DB
    ↓
Sends image + question to Gemini 2.0 Flash
    ↓
Gemini returns text description/analysis
    ↓
We store the analysis and return it to Claude
    ↓
Claude includes it in the chat response
```

```python
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[{
        "parts": [
            {"text": "Describe this image"},
            {"inline_data": {"mime_type": "image/png", "data": base64_string}},
        ]
    }],
)
```

---

## 8. Image Generation

### Flow

```
User asks "generate an image of X"
    ↓
Claude calls generate_image tool with prompt
    ↓
Our code tries Stability AI API (if key set)
    ↓
Falls back to mock (solid color PNG) if no key
    ↓
Stores image as base64 data URI in DB
    ↓
Returns image_id to Claude
    ↓
Claude confirms generation to user
```

The mock fallback means the app works even without a Stability AI key.

---

## 9. Memory System

### Why?

Without memory, each conversation is isolated. Memory lets Claude:
- Remember project decisions from past conversations
- Know the tech stack, goals, requirements without being told again
- Build up knowledge over time

### How It Works

```
Every chat request:
1. Load ALL project memories from DB
2. Format them into the system prompt
3. Claude sees them as context before responding
4. Claude can save NEW memories via save_memory tool
5. Claude can search memories via search_memory tool
```

### Memory Structure

Each memory entry has:
- `project_id` — scoped to one project
- `category` — goal, decision, requirement, reference, insight, context, task
- `key` — short identifier (e.g., "tech_stack", "launch_date")
- `content` — the actual knowledge
- `source` — who created it: "user", "assistant", or "agent"

### Scoping

Memory is **per-project**. Project A's memories are invisible to Project B.

---

## 10. Background Agent (Sub-agent)

### What It Does

Takes ALL project data and organizes it into structured memory entries.
Useful after many conversations — it extracts and categorizes everything important.

### How It Works

```
POST /api/agents/{project_id}/organize
    ↓
Creates a job record (status: "pending")
    ↓
Starts a background thread
    ↓
Returns job_id immediately (HTTP 202 Accepted)
    ↓
Background thread:
  1. Sets status → "running"
  2. Gathers: project, brief, all conversations, images, existing memory
  3. Sends everything to Claude with extraction instructions
  4. Claude outputs JSON lines of categorized knowledge
  5. Each entry is saved to project_memory table
  6. Sets status → "completed" (or "failed" with error)
    ↓
Client polls: GET /api/agents/jobs/{job_id}
  → {"status": "running"} ... {"status": "completed", "result": {...}}
```

### threading.Thread

```python
thread = threading.Thread(target=_run_agent, args=(project_id, job_id), daemon=True)
thread.start()
```

- `threading.Thread` — runs a function in a separate thread (non-blocking)
- `daemon=True` — thread dies when the main server stops
- The HTTP request returns immediately; the agent runs in the background

---

## 11. Project File Structure

```
novelty/
├── .env.example          # Template for environment variables
├── .env                  # Your actual keys (git-ignored)
├── requirements.txt      # Python dependencies
├── schema.sql            # Database table definitions (run in Supabase)
├── README.md             # Setup instructions and API reference
├── CONTEXT.md            # This file — full concept explanation
│
└── app/                  # Main application package
    ├── __init__.py       # Makes "app" a Python package
    ├── main.py           # FastAPI app creation + router registration
    ├── config.py         # Loads env vars from .env file
    ├── database.py       # Supabase client (shared DB connection)
    ├── models.py         # All Pydantic models (request/response shapes)
    │
    ├── routers/          # HTTP endpoint definitions (the "controllers")
    │   ├── __init__.py
    │   ├── projects.py   # /api/projects — CRUD for projects, briefs, conversations
    │   ├── chat.py       # /api/chat — send messages, get history
    │   ├── images.py     # /api/images — generate and analyze images
    │   ├── memory.py     # /api/memory — read/write/search project memory
    │   └── agents.py     # /api/agents — trigger background agent, poll status
    │
    └── services/         # Business logic (called by routers)
        ├── __init__.py
        ├── chat_service.py    # Claude chat with tool-use loop
        ├── memory_service.py  # Memory CRUD + formatting for context
        ├── image_service.py   # Image generation + Gemini analysis
        └── agent_service.py   # Background agent logic + threading
```

### Router vs Service pattern

- **Router** = defines HTTP endpoints, validates input, returns responses
- **Service** = does the actual work (DB queries, API calls, logic)
- Routers call services. Services don't know about HTTP.

---

## 12. Environment Variables (.env)

```bash
SUPABASE_URL=https://xyz.supabase.co    # Your Supabase project URL
SUPABASE_KEY=eyJ...                      # Supabase anon/public key
ANTHROPIC_API_KEY=sk-ant-...             # Claude API key
GEMINI_API_KEY=AI...                     # Google Gemini key (optional)
IMAGE_API_KEY=sk-...                     # Stability AI key (optional)
```

`python-dotenv` loads these from `.env` file into `os.environ` so your code
can read them with `os.getenv("KEY_NAME")`.

---

## 13. Request/Response Flow (End to End)

```
Client (curl/browser/frontend)
    │
    ▼
Uvicorn (HTTP server, port 8000)
    │
    ▼
FastAPI (routing, validation)
    │
    ▼
Router (e.g., chat.py — picks the right handler)
    │
    ▼
Service (e.g., chat_service.py — business logic)
    │
    ├──► Supabase (read/write database)
    ├──► Claude API (chat + tool use)
    ├──► Gemini API (image analysis)
    └──► Stability API (image generation)
    │
    ▼
Response JSON → Client
```

---

## 14. Key Dependencies (requirements.txt)

| Package            | What It Does                                                  |
| ------------------ | ------------------------------------------------------------- |
| `fastapi`          | Web framework — defines API endpoints                         |
| `uvicorn`          | ASGI server — runs the FastAPI app                            |
| `anthropic`        | Official Claude API client                                    |
| `google-genai`     | Official Gemini API client                                    |
| `supabase`         | Official Supabase Python client                               |
| `python-dotenv`    | Loads `.env` file into environment variables                  |
| `pydantic`         | Data validation (used by FastAPI for request/response models) |
| `httpx`            | HTTP client (used for Stability AI calls)                     |
| `Pillow`           | Image library (used for mock image generation)                |
| `python-multipart` | Handles file uploads in FastAPI                               |

---

## 15. Database Concepts in schema.sql

### UUID Primary Keys

```sql
id uuid primary key default uuid_generate_v4()
```

Every row gets a random unique ID like `a1b2c3d4-e5f6-...` instead of auto-incrementing numbers.

### Foreign Keys

```sql
project_id uuid not null references projects(id) on delete cascade
```

- `references projects(id)` — this column must contain a valid project ID
- `on delete cascade` — if the project is deleted, all related rows are deleted too

### Unique Constraints

```sql
unique(project_id, category, key)   -- in project_memory table
```

One project can't have two memories with the same category+key. Upsert uses this
to update instead of creating duplicates.

### Indexes

```sql
create index idx_messages_conversation on messages(conversation_id);
```

Makes queries filtering by `conversation_id` fast. Without indexes, the DB
scans every row.

### Triggers

```sql
create trigger trg_projects_updated before update on projects
    for each row execute function update_updated_at();
```

Automatically sets `updated_at = now()` whenever a row is updated.
