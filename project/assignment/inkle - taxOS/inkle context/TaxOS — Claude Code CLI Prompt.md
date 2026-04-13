# TaxOS — Claude Code CLI Prompt
# Paste everything below this line into your Claude Code session

---

## SYSTEM CONTEXT

You are building **TaxOS** — an AI-first US tax & compliance platform for startup founders.
Reference product: Inkle Tax (inkle.ai/tax). We are rebuilding it for an AI-first world.

**Core philosophy:**
- AI does 90% of the work. CPAs review. Founders only approve.
- Every AI action is logged, explainable, and reversible.
- Human-in-the-loop (HITL) is explicit, visible, and enforced — not implicit.
- No AI action with legal weight proceeds without a human gate.

---

## TECH STACK — STRICT

| Layer       | Choice                                          |
| ----------- | ----------------------------------------------- |
| Frontend    | React 18 + TypeScript + Vite                    |
| Styling     | Tailwind CSS v3 + shadcn/ui                     |
| State       | Zustand + React Query (TanStack Query v5)       |
| Backend     | Node.js + Express + TypeScript                  |
| ORM         | Drizzle ORM                                     |
| Database    | SQLite via better-sqlite3                       |
| AI          | Anthropic Claude API (claude-sonnet-4-20250514) |
| Auth        | JWT (jsonwebtoken) + bcrypt                     |
| File upload | Multer (local storage → /uploads)               |
| Validation  | Zod (shared between frontend and backend)       |
| API docs    | swagger-ui-express + zod-to-openapi             |

---

## PROJECT STRUCTURE

```
taxos/
├── apps/
│   ├── web/                        # React frontend (Vite)
│   │   ├── src/
│   │   │   ├── app/               # Route layout, providers
│   │   │   ├── pages/             # Route-level components
│   │   │   │   ├── CommandCenter.tsx
│   │   │   │   ├── FilingRoom.tsx
│   │   │   │   ├── ApprovalQueue.tsx
│   │   │   │   ├── AuditTrail.tsx
│   │   │   │   ├── DocumentVault.tsx
│   │   │   │   ├── AIAdvisor.tsx
│   │   │   │   ├── Entities.tsx
│   │   │   │   └── Deadlines.tsx
│   │   │   ├── components/        # Reusable UI components
│   │   │   │   ├── ui/            # shadcn primitives
│   │   │   │   ├── filing/        # Filing-specific components
│   │   │   │   ├── agents/        # Agent status, confidence UI
│   │   │   │   └── hitl/          # HITL gate components
│   │   │   ├── hooks/             # Custom React hooks
│   │   │   ├── stores/            # Zustand stores
│   │   │   ├── lib/               # API client, utils
│   │   │   └── types/             # Shared TS types
│   │   ├── index.html
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.ts
│   │   └── tsconfig.json
│   └── api/                        # Express backend
│       ├── src/
│       │   ├── db/
│       │   │   ├── schema.ts      # Drizzle schema (ALL tables)
│       │   │   ├── migrations/    # Drizzle migrations
│       │   │   └── seed.ts        # Seed data
│       │   ├── routes/
│       │   │   ├── auth.ts
│       │   │   ├── entities.ts
│       │   │   ├── filings.ts
│       │   │   ├── deadlines.ts
│       │   │   ├── documents.ts
│       │   │   ├── approvals.ts
│       │   │   ├── audit.ts
│       │   │   └── agents.ts      # AI agent trigger endpoints
│       │   ├── agents/
│       │   │   ├── base.ts        # Base agent class
│       │   │   ├── intake.ts      # Intake agent
│       │   │   ├── deadline.ts    # Deadline calculation agent
│       │   │   ├── document.ts    # Document extraction agent
│       │   │   ├── prefill.ts     # Form prefill agent
│       │   │   ├── auditRisk.ts   # Audit risk scoring agent
│       │   │   └── taxQa.ts       # Tax Q&A agent (RAG)
│       │   ├── middleware/
│       │   │   ├── auth.ts
│       │   │   ├── upload.ts
│       │   │   └── errorHandler.ts
│       │   ├── lib/
│       │   │   ├── anthropic.ts   # Anthropic client singleton
│       │   │   ├── auditLog.ts    # Immutable audit logger
│       │   │   └── deadlineEngine.ts
│       │   └── index.ts           # Express app entry
│       ├── taxos.db               # SQLite file (gitignored)
│       ├── uploads/               # File storage (gitignored)
│       └── tsconfig.json
├── packages/
│   └── shared/                    # Shared Zod schemas + types
│       ├── schemas/
│       │   ├── entity.ts
│       │   ├── filing.ts
│       │   ├── document.ts
│       │   └── agent.ts
│       └── index.ts
├── package.json                   # Root workspace
└── .env.example
```

---

## PHASE 1 — SCAFFOLD & DATABASE

### Step 1: Initialize monorepo

```bash
mkdir taxos && cd taxos
npm init -y
# Set up pnpm workspaces
```

Create `package.json` at root:
```json
{
  "name": "taxos",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev": "concurrently \"pnpm --filter api dev\" \"pnpm --filter web dev\"",
    "build": "pnpm --filter api build && pnpm --filter web build",
    "db:migrate": "pnpm --filter api db:migrate",
    "db:seed": "pnpm --filter api db:seed"
  }
}
```

### Step 2: Database Schema (apps/api/src/db/schema.ts)

Build ALL tables using Drizzle ORM with SQLite:

```typescript
import { sqliteTable, text, integer, real, blob } from 'drizzle-orm/sqlite-core'
import { sql } from 'drizzle-orm'

// ─── Organizations ────────────────────────────────────
export const organizations = sqliteTable('organizations', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  name: text('name').notNull(),
  plan: text('plan', { enum: ['free', 'starter', 'pro'] }).default('free').notNull(),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Users ────────────────────────────────────────────
export const users = sqliteTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  email: text('email').unique().notNull(),
  passwordHash: text('password_hash').notNull(),
  name: text('name').notNull(),
  role: text('role', { enum: ['founder', 'team_member', 'cpa', 'admin'] }).default('founder').notNull(),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Entities ─────────────────────────────────────────
export const entities = sqliteTable('entities', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  legalName: text('legal_name').notNull(),
  entityType: text('entity_type', { enum: ['C-Corp', 'LLC', 'S-Corp', 'Pvt-Ltd'] }).notNull(),
  stateOfIncorporation: text('state_of_incorporation').notNull(),
  ein: text('ein'),
  fiscalYearEnd: text('fiscal_year_end').default('12-31').notNull(),
  foreignSubsidiaries: text('foreign_subsidiaries', { mode: 'json' }).$type<string[]>().default([]),
  country: text('country').default('US').notNull(),
  status: text('status', { enum: ['active', 'inactive', 'dissolved'] }).default('active').notNull(),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Deadlines ────────────────────────────────────────
export const deadlines = sqliteTable('deadlines', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  entityId: text('entity_id').references(() => entities.id).notNull(),
  formType: text('form_type').notNull(), // '1120', '5471', 'DFT', etc.
  formName: text('form_name').notNull(), // Human readable name
  dueDate: text('due_date').notNull(),   // ISO date string
  status: text('status', { enum: ['upcoming', 'overdue', 'filed', 'extended'] }).default('upcoming').notNull(),
  aiPredicted: integer('ai_predicted', { mode: 'boolean' }).default(true),
  urgencyScore: integer('urgency_score').default(0), // 0–100
  description: text('description'),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Filings ──────────────────────────────────────────
export const filings = sqliteTable('filings', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  entityId: text('entity_id').references(() => entities.id).notNull(),
  deadlineId: text('deadline_id').references(() => deadlines.id),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  formType: text('form_type').notNull(),
  formName: text('form_name').notNull(),
  status: text('status', {
    enum: ['intake', 'ai_prep', 'cpa_review', 'founder_approval', 'submitted', 'archived']
  }).default('intake').notNull(),
  aiConfidenceScore: real('ai_confidence_score'),   // 0.0 to 1.0
  cpaAssignedId: text('cpa_assigned_id').references(() => users.id),
  filingData: text('filing_data', { mode: 'json' }).$type<Record<string, unknown>>().default({}),
  aiSummary: text('ai_summary'),                     // AI-generated plain English summary
  aiReasoning: text('ai_reasoning'),                 // Why AI did what it did
  founderApprovedAt: text('founder_approved_at'),
  submittedAt: text('submitted_at'),
  taxYear: integer('tax_year'),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedAt: text('updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Documents ────────────────────────────────────────
export const documents = sqliteTable('documents', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  filingId: text('filing_id').references(() => filings.id),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  fileName: text('file_name').notNull(),
  storageUrl: text('storage_url').notNull(),
  mimeType: text('mime_type').notNull(),
  extractedData: text('extracted_data', { mode: 'json' }).$type<Record<string, unknown>>(),
  aiTags: text('ai_tags', { mode: 'json' }).$type<string[]>().default([]),
  confidenceScore: real('confidence_score'),
  reviewedByHuman: integer('reviewed_by_human', { mode: 'boolean' }).default(false),
  uploadedById: text('uploaded_by_id').references(() => users.id).notNull(),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Approval Queue ───────────────────────────────────
export const approvalQueue = sqliteTable('approval_queue', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  filingId: text('filing_id').references(() => filings.id).notNull(),
  queueType: text('queue_type', { enum: ['founder', 'cpa'] }).notNull(),
  status: text('status', { enum: ['pending', 'approved', 'rejected', 'escalated'] }).default('pending').notNull(),
  summary: text('summary').notNull(),       // AI-written plain English, max 3 sentences
  aiRecommendation: text('ai_recommendation'),
  rejectionReason: text('rejection_reason'),
  resolvedAt: text('resolved_at'),
  resolvedById: text('resolved_by_id').references(() => users.id),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Audit Log (immutable) ────────────────────────────
export const auditLog = sqliteTable('audit_log', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  filingId: text('filing_id').references(() => filings.id),
  actorType: text('actor_type', { enum: ['ai', 'cpa', 'founder', 'system'] }).notNull(),
  actorId: text('actor_id'),                // userId or 'ai-agent-name'
  action: text('action').notNull(),         // e.g. 'form_prefilled', 'founder_approved'
  reasoning: text('reasoning'),             // AI must always provide reasoning
  inputs: text('inputs', { mode: 'json' }).$type<Record<string, unknown>>(),
  outputs: text('outputs', { mode: 'json' }).$type<Record<string, unknown>>(),
  modelVersion: text('model_version'),      // e.g. 'claude-sonnet-4-20250514'
  confidenceScore: real('confidence_score'),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})

// ─── Agent Conversations ──────────────────────────────
export const agentConversations = sqliteTable('agent_conversations', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  filingId: text('filing_id').references(() => filings.id),
  orgId: text('org_id').references(() => organizations.id).notNull(),
  agentType: text('agent_type').notNull(), // 'intake', 'tax_qa', 'prefill', etc.
  messages: text('messages', { mode: 'json' }).$type<Array<{role: string, content: string, timestamp: string}>>().default([]),
  status: text('status', { enum: ['active', 'completed', 'escalated'] }).default('active').notNull(),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedAt: text('updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})
```

---

## PHASE 2 — BACKEND API ROUTES

### Auth (apps/api/src/routes/auth.ts)

```typescript
// POST /api/auth/register   — create org + founder user
// POST /api/auth/login      — returns JWT
// GET  /api/auth/me         — returns current user from JWT
```

Implement proper JWT middleware that extracts `userId`, `orgId`, `role` from token and attaches to `req.user`.

### Entities (apps/api/src/routes/entities.ts)

```typescript
// GET    /api/entities          — list all entities for org
// POST   /api/entities          — create entity (triggers deadline agent)
// GET    /api/entities/:id      — get entity details
// PUT    /api/entities/:id      — update entity
// DELETE /api/entities/:id      — soft delete
```

### Filings (apps/api/src/routes/filings.ts)

```typescript
// GET    /api/filings            — list all filings (with filters: status, entity, year)
// POST   /api/filings            — create filing (intake stage)
// GET    /api/filings/:id        — get filing details + conversation + documents
// PUT    /api/filings/:id/status — advance filing status (with HITL gate check)
// POST   /api/filings/:id/approve — founder approves filing
// POST   /api/filings/:id/reject  — founder rejects filing (with reason)
```

### AI Agents (apps/api/src/routes/agents.ts)

```typescript
// POST /api/agents/intake/start     — start intake conversation for a filing
// POST /api/agents/intake/message   — send message to intake agent (streaming)
// POST /api/agents/deadline/run     — recalculate deadlines for entity
// POST /api/agents/document/extract — extract data from uploaded document
// POST /api/agents/prefill/run      — run form prefill agent for a filing
// POST /api/agents/audit-risk/run   — score audit risk for a filing
// POST /api/agents/tax-qa/ask       — ask the tax Q&A agent (streaming)
```

### Approvals (apps/api/src/routes/approvals.ts)

```typescript
// GET  /api/approvals          — list pending approvals for current user
// POST /api/approvals/:id/resolve — approve or reject (with reason)
// POST /api/approvals/:id/escalate — escalate to CPA
```

---

## PHASE 3 — AI AGENTS

### Base Agent Pattern (apps/api/src/agents/base.ts)

```typescript
import Anthropic from '@anthropic-ai/sdk'
import { db } from '../db'
import { auditLog } from '../db/schema'
import { auditLogger } from '../lib/auditLog'

export abstract class BaseAgent {
  protected client: Anthropic
  protected modelVersion = 'claude-sonnet-4-20250514'

  constructor() {
    this.client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  }

  // Every agent must log its actions
  protected async log(params: {
    orgId: string
    filingId?: string
    action: string
    reasoning: string
    inputs: Record<string, unknown>
    outputs: Record<string, unknown>
    confidenceScore?: number
  }) {
    return auditLogger.log({
      ...params,
      actorType: 'ai',
      actorId: `agent:${this.constructor.name}`,
      modelVersion: this.modelVersion,
    })
  }

  // Confidence check — if below threshold, escalate to CPA
  protected shouldEscalate(score: number, threshold = 0.75): boolean {
    return score < threshold
  }
}
```

### Intake Agent (apps/api/src/agents/intake.ts)

```typescript
// This agent conducts a conversational interview with the founder
// to collect all required information for a filing.
// It uses Claude's streaming API for real-time responses.

const INTAKE_SYSTEM_PROMPT = `
You are TaxOS Intake Agent, an expert US tax assistant conducting a filing intake interview.

Your job is to collect all required information for the specified filing type through
a natural conversation — NOT a form. Ask one question at a time. Be friendly, clear,
and avoid jargon. If the founder uses a term incorrectly, gently correct them.

Rules:
1. Ask ONLY one question per message
2. Acknowledge the previous answer before asking the next question
3. If an answer is ambiguous, ask for clarification
4. When you have all required data, output a JSON block starting with "INTAKE_COMPLETE:"
5. Always explain WHY you need each piece of information
6. If the founder asks a tax question, answer it briefly then return to the intake

Filing type: {FORM_TYPE}
Required fields: {REQUIRED_FIELDS}
Entity context: {ENTITY_CONTEXT}
`

export class IntakeAgent extends BaseAgent {
  async startConversation(filingId: string, formType: string, entityContext: object) {
    // Initialize conversation, return first question
  }

  async *streamMessage(filingId: string, userMessage: string): AsyncGenerator<string> {
    // Stream Claude's response token by token
    // When INTAKE_COMPLETE detected, trigger form prefill agent
  }
}
```

### Deadline Agent (apps/api/src/agents/deadline.ts)

```typescript
// Calculates deadlines for all applicable filings based on entity characteristics
// Uses a rule engine first, then Claude for edge cases

const DEADLINE_RULES = {
  'C-Corp': {
    '1120': { baseMonth: 4, baseDay: 15, extensionAvailable: true, extensionForm: '7004' },
    '5472': { baseMonth: 4, baseDay: 15, extensionAvailable: false },
    '5471': { baseMonth: 4, baseDay: 15, extensionAvailable: true },
    'DFT': { baseMonth: 3, baseDay: 1, extensionAvailable: false }, // Delaware Franchise Tax
  },
  // Add more entity types...
}

export class DeadlineAgent extends BaseAgent {
  async calculateDeadlines(entityId: string): Promise<void> {
    // 1. Fetch entity details
    // 2. Apply rule-based deadline engine for known forms
    // 3. Use Claude for complex multi-state or foreign filing scenarios
    // 4. Calculate urgency scores (days until due, 0-100)
    // 5. Upsert deadlines to DB
    // 6. Log all actions with reasoning
  }

  private urgencyScore(dueDate: string): number {
    const days = Math.ceil((new Date(dueDate).getTime() - Date.now()) / 86_400_000)
    if (days < 0) return 100      // overdue
    if (days < 7) return 95
    if (days < 30) return 80
    if (days < 60) return 60
    if (days < 90) return 40
    return 20
  }
}
```

### Document Extraction Agent (apps/api/src/agents/document.ts)

```typescript
const EXTRACTION_PROMPT = `
You are a document extraction specialist. Extract all structured data from this tax document.

Return a JSON object with:
{
  "documentType": "string (e.g. W-2, 1099-NEC, bank statement)",
  "taxYear": number,
  "fields": {
    "fieldName": {
      "value": "extracted value",
      "confidence": 0.0-1.0,
      "pageNumber": number
    }
  },
  "overallConfidence": 0.0-1.0,
  "flaggedIssues": ["any anomalies or unclear data"],
  "reasoning": "brief explanation of extraction approach"
}

Mark confidence < 0.75 for any field that is unclear, partially visible, or ambiguous.
`

export class DocumentAgent extends BaseAgent {
  async extractFromPdf(documentId: string, pdfBase64: string) {
    // Send to Claude vision API
    // Parse structured response
    // If overall confidence < 0.75, flag for human review
    // Update document record with extracted data
    // Create audit log entry
    // If low confidence fields exist, create CPA approval queue item
  }
}
```

### Form Prefill Agent (apps/api/src/agents/prefill.ts)

```typescript
const PREFILL_PROMPT = `
You are a US tax form preparation specialist.

Given:
- Entity information: {ENTITY_DATA}
- Intake responses: {INTAKE_DATA}
- Extracted documents: {DOCUMENT_DATA}
- Prior year filing (if available): {PRIOR_FILING}

Prefill the following form fields for {FORM_TYPE}:
{FORM_FIELDS}

For each field return:
{
  "fieldId": {
    "value": "computed value",
    "confidence": 0.0-1.0,
    "source": "which data source this came from",
    "reasoning": "why this value was computed this way",
    "needsCpaReview": boolean
  }
}

Flag needsCpaReview=true if:
- Confidence < 0.8
- The field involves a judgment call (not a pure calculation)
- The value differs significantly from prior year
- It involves foreign transactions or assets
`

export class PrefillAgent extends BaseAgent {
  async prefillForm(filingId: string) {
    // Gather all context
    // Call Claude with form-specific prompts
    // Store prefilled data + confidence scores
    // If any needsCpaReview=true fields, create CPA queue item
    // Advance filing status to 'cpa_review'
    // Log everything
  }
}
```

### Audit Risk Agent (apps/api/src/agents/auditRisk.ts)

```typescript
const AUDIT_RISK_PROMPT = `
You are a US tax audit risk specialist.

Analyze this {FORM_TYPE} filing for audit risk factors:

Filing data: {FILING_DATA}
Entity profile: {ENTITY_DATA}
Industry benchmarks: {available if known}

Return:
{
  "overallRiskScore": 0-100,
  "riskLevel": "low|medium|high|critical",
  "flaggedItems": [
    {
      "lineItem": "field/line reference",
      "issue": "description of concern",
      "severity": "low|medium|high",
      "recommendation": "what to do"
    }
  ],
  "reasoning": "overall assessment"
}

Risk score guide: 0-30=low, 31-60=medium, 61-85=high, 86-100=critical
If riskScore > 60, mandatory CPA review is required.
`

export class AuditRiskAgent extends BaseAgent {
  async scoreRisk(filingId: string) {
    // Run risk analysis
    // If score > 60, block submission and create mandatory CPA queue item
    // Log result with full reasoning
    // Return risk report
  }
}
```

### Tax Q&A Agent (apps/api/src/agents/taxQa.ts)

```typescript
const TAX_QA_SYSTEM_PROMPT = `
You are TaxOS AI Advisor — a knowledgeable US tax assistant for startup founders.

You have context about the founder's specific entities and filings.
Always:
1. Answer in plain English — no unexplained jargon
2. Cite your source (IRS publication, IRC section, state code)
3. Provide a confidence level: HIGH/MEDIUM/LOW
4. If the question involves penalty exposure, amended returns, or significant financial risk,
   set requiresCpaReview=true
5. Never give a definitive answer on complex planning questions — recommend CPA consultation

Entity context: {ENTITY_CONTEXT}
Active filings: {FILING_CONTEXT}

Format response as:
{
  "answer": "plain English answer",
  "sources": ["IRS Pub 535", "IRC §162", etc.],
  "confidence": "HIGH|MEDIUM|LOW",
  "requiresCpaReview": boolean,
  "cpaEscalationReason": "if requiresCpaReview is true, why"
}
`

export class TaxQaAgent extends BaseAgent {
  async *streamAnswer(orgId: string, question: string): AsyncGenerator<string> {
    // Stream response from Claude
    // Parse final JSON for confidence/escalation metadata
    // Log the Q&A interaction
  }
}
```

---

## PHASE 4 — FRONTEND UI

### Design System Rules

**Colors:**
- Primary: `#6C5CE7` (purple — matching Inkle's brand feel)
- Success: `#00B894`
- Warning: `#FDCB6E`
- Danger: `#E17055`
- Neutral: `#636E72`

**Filing status colors:**
```typescript
export const STATUS_COLORS = {
  intake:            { bg: 'bg-gray-100',   text: 'text-gray-700',   label: 'Intake' },
  ai_prep:           { bg: 'bg-blue-100',   text: 'text-blue-700',   label: 'AI Prep' },
  cpa_review:        { bg: 'bg-amber-100',  text: 'text-amber-700',  label: 'CPA Review' },
  founder_approval:  { bg: 'bg-orange-100', text: 'text-orange-700', label: 'Needs Approval' },
  submitted:         { bg: 'bg-green-100',  text: 'text-green-700',  label: 'Submitted' },
  archived:          { bg: 'bg-gray-100',   text: 'text-gray-500',   label: 'Archived' },
} as const
```

**Confidence indicator component:**
```tsx
// Show on every AI output
function ConfidenceBadge({ score }: { score: number }) {
  if (score >= 0.85) return <Badge className="bg-green-100 text-green-700">✓ AI confident</Badge>
  if (score >= 0.75) return <Badge className="bg-amber-100 text-amber-700">⚠ CPA review recommended</Badge>
  return <Badge className="bg-red-100 text-red-700">⚡ CPA must verify</Badge>
}
```

### Pages to Build

#### 1. Command Center (pages/CommandCenter.tsx)

```
Layout:
┌─────────────────────────────────────────────────┐
│  URGENCY STRIP: Items needing attention TODAY    │
├────────────────────┬────────────────────────────┤
│ FILING PIPELINE    │ NEXT 3 DEADLINES            │
│ (Kanban columns)   │ (countdown timer cards)     │
│                    ├────────────────────────────┤
│                    │ AI ACTIVITY FEED            │
│                    │ (real-time agent actions)   │
├────────────────────┴────────────────────────────┤
│ APPROVAL QUEUE PREVIEW (red badge if pending)    │
└─────────────────────────────────────────────────┘
```

- Kanban board with 6 columns (one per filing status)
- Each card shows: form type, entity, deadline countdown, confidence score
- Activity feed shows last 10 AI agent actions with timestamps
- Urgency strip highlights anything due within 7 days or overdue

#### 2. Filing Room (pages/FilingRoom.tsx)

```
Layout:
┌──────────────┬─────────────────────┬────────────┐
│ TIMELINE     │ AI CONVERSATION     │ FORM       │
│ SIDEBAR      │ THREAD              │ PREVIEW    │
│              │ (chat-style intake, │            │
│ Stage 1 ✓   │  updates, Q&A)      │ (prefilled │
│ Stage 2 ✓   │                     │  draft)    │
│ Stage 3 ⟳   │                     │            │
│ Stage 4 ...  │─────────────────────│            │
│              │ DOCUMENT PANEL      │            │
│              │ (uploads + extracts)│            │
└──────────────┴─────────────────────┴────────────┘
│ APPROVAL CARD (founder e-sign gate)              │
└─────────────────────────────────────────────────┘
```

- Left sidebar: visual timeline of all filing stages
- Center: streaming chat with AI agents — intake conversation, status updates
- Right: form preview with prefilled fields + confidence highlights
- Bottom: approval card appears at 'founder_approval' stage

#### 3. Approval Queue (pages/ApprovalQueue.tsx)

Each card shows:
- Filing type + entity name
- AI-written summary (max 3 sentences, plain English)
- What the AI did and why
- What the founder needs to decide
- Confidence score badge
- 4 action buttons: **Approve** | **Reject** | **Ask AI** | **Get CPA**

`Ask AI` opens an inline chat panel.
`Get CPA` triggers escalation and creates CPA queue item.

#### 4. AI Advisor (pages/AIAdvisor.tsx)

- Full-width streaming chat interface
- Source citations displayed under each answer
- Confidence badge on every response
- "Escalate to CPA" button shown if `requiresCpaReview=true`
- "Save to filing context" button to attach answers to a specific filing

#### 5. Audit Trail (pages/AuditTrail.tsx)

- Filter by: filing, actor type (AI/CPA/Founder), date range
- Each entry shows: timestamp, actor, action, reasoning, confidence, inputs/outputs
- Export as CSV button
- Color-coded by actor type:
  - AI actions: blue
  - CPA actions: amber
  - Founder actions: green

#### 6. Document Vault (pages/DocumentVault.tsx)

- Drag-and-drop upload zone
- After upload: auto-extraction runs, shows extracted fields with confidence
- Low-confidence fields highlighted in amber with "Needs review" flag
- AI tags shown as chips on each document
- Filter by: filing, document type, review status

---

## PHASE 5 — HUMAN-IN-THE-LOOP (HITL) GATES

### Gate enforcement rules (CRITICAL)

**In the backend, enforce these as middleware:**

```typescript
// filings.ts - status transition guard
export function validateStatusTransition(current: FilingStatus, next: FilingStatus, userRole: string) {
  const ALLOWED_TRANSITIONS: Record<FilingStatus, FilingStatus[]> = {
    intake:           ['ai_prep'],
    ai_prep:          ['cpa_review', 'intake'],  // can go back to intake if data missing
    cpa_review:       ['founder_approval', 'ai_prep'],
    founder_approval: ['submitted', 'cpa_review'],
    submitted:        ['archived'],
    archived:         [],
  }

  // HITL Rules — block if gates not cleared
  if (next === 'submitted') {
    // Must have: founder_approved_at, cpa sign-off, risk score <= 85
    throw new Error('Cannot submit without founder approval and CPA sign-off')
  }
  if (next === 'founder_approval' && userRole === 'founder') {
    throw new Error('CPA must advance filing to founder approval stage')
  }
}
```

**AI can never:**
- Submit any filing (HTTP 403 if attempted)
- Create approval queue items and auto-resolve them
- Delete or modify documents
- Make payments

**Founder can always:**
- Pause any AI workflow: `POST /api/filings/:id/pause`
- Request CPA takeover: `POST /api/filings/:id/escalate-cpa`
- Download full audit trail: `GET /api/filings/:id/audit-trail/export`

---

## PHASE 6 — SEED DATA

Create realistic seed data in `apps/api/src/db/seed.ts`:

```typescript
// Create demo org: "Acme Inc (Demo)"
// Create founder user: demo@taxos.ai / password: demo1234
// Create 2 entities:
//   - Acme Inc (C-Corp, Delaware)
//   - Acme India Pvt Ltd (foreign subsidiary)
// Create deadlines for tax year 2025:
//   - Form 1120 (due Apr 15, 2026) — urgency: 95
//   - Form 5472 (due Apr 15, 2026) — urgency: 95
//   - Form 5471 (due Apr 15, 2026) — urgency: 90
//   - Delaware Franchise Tax (due Mar 1, 2026) — OVERDUE — urgency: 100
//   - Form 7004 Extension (due Apr 15, 2026) — urgency: 80
// Create filings in various stages:
//   - Form 1120 at 'cpa_review' (with AI confidence 0.88)
//   - Form 5472 at 'founder_approval' (with approval queue item)
//   - Form 7004 at 'ai_prep'
// Create 2 pending approval queue items
// Create 15 audit log entries showing the lifecycle
```

---

## PHASE 7 — ENVIRONMENT SETUP

`.env.example`:
```env
# API
NODE_ENV=development
PORT=3001
DATABASE_URL=./taxos.db
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
ANTHROPIC_API_KEY=sk-ant-...

# Frontend
VITE_API_URL=http://localhost:3001/api
```

---

## FINAL CHECKLIST

Build in this order:
- [ ] Monorepo scaffold (pnpm workspaces)
- [ ] Shared Zod schemas package
- [ ] DB schema + migrations + seed
- [ ] Express server with auth middleware
- [ ] All REST routes (entities, filings, deadlines, documents, approvals, audit)
- [ ] Base agent class + audit logger
- [ ] All 6 AI agents (intake, deadline, document, prefill, auditRisk, taxQa)
- [ ] HITL gate enforcement middleware
- [ ] React app setup (Vite + Tailwind + shadcn)
- [ ] Sidebar navigation (matching Inkle's layout)
- [ ] Command Center page
- [ ] Filing Room page (with streaming chat)
- [ ] Approval Queue page
- [ ] AI Advisor page (streaming)
- [ ] Audit Trail page
- [ ] Document Vault page
- [ ] Entities page
- [ ] Confidence badge component (used everywhere)
- [ ] Demo login page
- [ ] README with setup + demo walkthrough

---

## HOW TO RUN CLAUDE CODE

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Navigate to your project directory
mkdir taxos && cd taxos

# Launch Claude Code with this prompt
claude "$(cat TAXOS_CLAUDE_CODE_PROMPT.md)"

# Or start interactively and paste this file's contents
claude
```

Then paste this entire document into the Claude Code session.
Claude Code will read the full spec and begin building the application.
It will ask for clarification only when genuinely ambiguous — otherwise it builds.

---

## DEMO VIDEO SCRIPT (what to record)

1. **Login** as demo@taxos.ai
2. **Command Center** — show urgency strip, kanban, deadlines, AI feed
3. **Approval Queue** — show pending Form 5472, AI summary, click "Approve"
4. **Filing Room** — open Form 1120, show chat thread, confidence badges, CPA notes
5. **Start intake** — start a new Form 1099 filing, chat with AI intake agent (streaming)
6. **Document Vault** — upload a PDF, watch AI extract fields with confidence scores
7. **AI Advisor** — ask "Do I need to file Form 5471?" — watch streaming answer with source
8. **Audit Trail** — filter by AI actor, show full reasoning log, export CSV