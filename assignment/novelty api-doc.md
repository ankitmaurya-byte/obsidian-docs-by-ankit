# Novelty AI Project Assistant - API Documentation

**Base URL:** `http://localhost:8000`

---

## Table of Contents

- [Health Check](#health-check)
- [Projects](#projects)
- [Project Briefs](#project-briefs)
- [Conversations](#conversations)
- [Chat](#chat)
- [Images](#images)
- [Memory](#memory)
- [Agents](#agents)

---

## Health Check

### `GET /`

Check if the server is running.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{ "name": "Novelty", "status": "running" }
```

---

## Projects

### List All Projects

`GET /api/projects/`

```bash
curl http://localhost:8000/api/projects/
```

### Create a Project

`POST /api/projects/`

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Startup App",
    "description": "A mobile app for habit tracking",
    "status": "active"
  }'
```

| Field         | Type   | Required | Default    | Notes                                  |
|---------------|--------|----------|------------|----------------------------------------|
| `name`        | string | Yes      | -          |                                        |
| `description` | string | No       | `null`     |                                        |
| `status`      | string | No       | `"active"` | One of: `active`, `archived`, `completed` |

### Get a Project

`GET /api/projects/{project_id}`

```bash
curl http://localhost:8000/api/projects/PROJECT_ID
```

### Update a Project

`PATCH /api/projects/{project_id}`

```bash
curl -X PATCH http://localhost:8000/api/projects/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Startup App v2",
    "status": "completed"
  }'
```

### Delete a Project

`DELETE /api/projects/{project_id}`

```bash
curl -X DELETE http://localhost:8000/api/projects/PROJECT_ID
```

**Response:** `204 No Content`

---

## Project Briefs

Each project has a single brief containing goals, audience, constraints, etc.

### Get Brief

`GET /api/projects/{project_id}/brief`

```bash
curl http://localhost:8000/api/projects/PROJECT_ID/brief
```

### Create Brief

`POST /api/projects/{project_id}/brief`

```bash
curl -X POST http://localhost:8000/api/projects/PROJECT_ID/brief \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Habit Tracker MVP",
    "description": "Build an MVP for a daily habit tracking app",
    "goals": ["Track daily habits", "Send reminders", "Show streaks"],
    "target_audience": "Young professionals aged 20-35",
    "reference_links": ["https://example.com/competitor-analysis"],
    "constraints": "Budget: $5000, Timeline: 4 weeks",
    "tags": ["mobile", "productivity", "MVP"]
  }'
```

| Field              | Type     | Required | Default | Notes              |
|--------------------|----------|----------|---------|--------------------|
| `title`            | string   | Yes      | -       |                    |
| `description`      | string   | No       | `null`  |                    |
| `goals`            | string[] | No       | `null`  | Array of strings   |
| `target_audience`  | string   | No       | `null`  |                    |
| `reference_links`  | string[] | No       | `null`  | Array of URLs      |
| `constraints`      | string   | No       | `null`  |                    |
| `tags`             | string[] | No       | `null`  |                    |

### Update Brief

`PATCH /api/projects/{project_id}/brief`

```bash
curl -X PATCH http://localhost:8000/api/projects/PROJECT_ID/brief \
  -H "Content-Type: application/json" \
  -d '{
    "goals": ["Track daily habits", "Send reminders", "Show streaks", "Export data"]
  }'
```

---

## Conversations

### List Conversations for a Project

`GET /api/projects/{project_id}/conversations`

```bash
curl http://localhost:8000/api/projects/PROJECT_ID/conversations
```

### Create a Conversation

`POST /api/projects/{project_id}/conversations`

```bash
curl -X POST http://localhost:8000/api/projects/PROJECT_ID/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Brainstorming session"
  }'
```

| Field   | Type   | Required | Default | Notes |
|---------|--------|----------|---------|-------|
| `title` | string | No       | `null`  |       |

---

## Chat

### Send a Message

`POST /api/chat/{project_id}`

Sends a message to the AI assistant within a project context. If `conversation_id` is omitted, a new conversation is created automatically.

```bash
# New conversation (auto-created)
curl -X POST http://localhost:8000/api/chat/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me plan the tech stack for my habit tracker app"
  }'
```

```bash
# Continue an existing conversation
curl -X POST http://localhost:8000/api/chat/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about using React Native for the frontend?",
    "conversation_id": "CONVERSATION_ID"
  }'
```

| Field             | Type   | Required | Default | Notes                                 |
|-------------------|--------|----------|---------|---------------------------------------|
| `message`         | string | Yes      | -       | The user message to send              |
| `conversation_id` | string | No       | `null`  | Omit to auto-create a new conversation |

**Response:**
```json
{
  "conversation_id": "uuid",
  "response": "Here's my recommendation for your tech stack...",
  "tool_calls": null
}
```

### Get Messages in a Conversation

`GET /api/chat/{project_id}/conversations/{conversation_id}/messages`

```bash
curl http://localhost:8000/api/chat/PROJECT_ID/conversations/CONVERSATION_ID/messages
```

---

## Images

### List Images for a Project

`GET /api/images/{project_id}`

```bash
curl http://localhost:8000/api/images/PROJECT_ID
```

### Generate an Image

`POST /api/images/{project_id}/generate`

```bash
curl -X POST http://localhost:8000/api/images/PROJECT_ID/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A clean minimal UI mockup for a habit tracking app with a dark theme"
  }'
```

```bash
# Link to a conversation
curl -X POST http://localhost:8000/api/images/PROJECT_ID/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Logo design for a habit tracker called StreakMaster",
    "conversation_id": "CONVERSATION_ID"
  }'
```

| Field             | Type   | Required | Default | Notes                         |
|-------------------|--------|----------|---------|-------------------------------|
| `prompt`          | string | Yes      | -       | Image generation prompt       |
| `conversation_id` | string | No       | `null`  | Link the image to a conversation |

### Analyze an Image

`POST /api/images/analyze`

Uses Gemini to analyze a previously generated image.

```bash
curl -X POST http://localhost:8000/api/images/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "IMAGE_ID",
    "question": "What colors and layout patterns are used in this design?"
  }'
```

| Field      | Type   | Required | Default                            | Notes |
|------------|--------|----------|------------------------------------|-------|
| `image_id` | string | Yes      | -                                  |       |
| `question` | string | No       | `"Describe this image in detail."` |       |

**Response:**
```json
{
  "image_id": "uuid",
  "analysis": "The image features a dark-themed UI with..."
}
```

---

## Memory

Per-project knowledge store. Memories are categorized and keyed (unique per project + category + key).

### List Memories

`GET /api/memory/{project_id}`

```bash
# All memories
curl http://localhost:8000/api/memory/PROJECT_ID

# Filter by category
curl "http://localhost:8000/api/memory/PROJECT_ID?category=decision"
```

### Create / Upsert a Memory

`POST /api/memory/{project_id}`

If a memory with the same `project_id` + `category` + `key` exists, it will be updated (upsert).

```bash
curl -X POST http://localhost:8000/api/memory/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "category": "decision",
    "key": "tech-stack",
    "content": "Using React Native + Supabase for the habit tracker MVP",
    "source": "user"
  }'
```

| Field      | Type   | Required | Default    | Notes                                                        |
|------------|--------|----------|------------|--------------------------------------------------------------|
| `category` | string | Yes      | -          | e.g. `goal`, `decision`, `reference`, `insight`, `requirement` |
| `key`      | string | Yes      | -          | Short identifier, unique within project + category           |
| `content`  | string | Yes      | -          | The memory content                                           |
| `source`   | string | No       | `"user"`   | Where this came from: `user`, `conversation`, `agent`        |

### Search Memories

`GET /api/memory/{project_id}/search?q={keyword}`

Simple keyword search (case-insensitive) across memory content.

```bash
curl "http://localhost:8000/api/memory/PROJECT_ID/search?q=react"
```

### Delete a Memory

`DELETE /api/memory/{project_id}/{memory_id}`

```bash
curl -X DELETE http://localhost:8000/api/memory/PROJECT_ID/MEMORY_ID
```

**Response:** `204 No Content`

---

## Agents

Background agents that process and organize project data.

### Trigger Organize Agent

`POST /api/agents/{project_id}/organize`

Triggers a background agent to organize project conversations into structured memory entries.

```bash
curl -X POST http://localhost:8000/api/agents/PROJECT_ID/organize
```

**Response (`202 Accepted`):**
```json
{
  "id": "job-uuid",
  "project_id": "project-uuid",
  "job_type": "organize_memory",
  "status": "pending",
  "result": null,
  "error": null,
  "started_at": null,
  "completed_at": null,
  "created_at": "2026-03-31T10:00:00Z"
}
```

### Poll Job Status

`GET /api/agents/jobs/{job_id}`

```bash
curl http://localhost:8000/api/agents/jobs/JOB_ID
```

### List Jobs for a Project

`GET /api/agents/{project_id}/jobs`

```bash
curl http://localhost:8000/api/agents/PROJECT_ID/jobs
```

---

## Full Workflow Example

A typical end-to-end usage flow:

```bash
# 1. Create a project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Habit Tracker", "description": "Daily habit tracking app"}'
# Save the returned "id" as PROJECT_ID

# 2. Add a brief
curl -X POST http://localhost:8000/api/projects/PROJECT_ID/brief \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Habit Tracker MVP",
    "goals": ["Track habits", "Show streaks"],
    "target_audience": "Young professionals"
  }'

# 3. Chat with the AI assistant
curl -X POST http://localhost:8000/api/chat/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "Suggest a tech stack for this project"}'
# Save the returned "conversation_id" as CONV_ID

# 4. Continue the conversation
curl -X POST http://localhost:8000/api/chat/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "What about the database layer?", "conversation_id": "CONV_ID"}'

# 5. Generate a UI mockup
curl -X POST http://localhost:8000/api/images/PROJECT_ID/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Minimal habit tracker app home screen"}'

# 6. Save a decision to memory
curl -X POST http://localhost:8000/api/memory/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{"category": "decision", "key": "database", "content": "Using Supabase PostgreSQL"}'

# 7. Run the organize agent
curl -X POST http://localhost:8000/api/agents/PROJECT_ID/organize
# Save the returned "id" as JOB_ID

# 8. Check agent job status
curl http://localhost:8000/api/agents/jobs/JOB_ID
```
