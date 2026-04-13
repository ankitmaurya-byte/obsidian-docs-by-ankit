---
title: "TaxOS — AI-First Tax Platform for Founders"
aliases:
  - TaxOS
  - AI Tax App
  - Inkle Reimagined
tags:
  - project/taxos
  - ai/agents
  - compliance
  - founders
  - product-design
  - human-in-the-loop
created: 2026-04-03
status: planning
stage: pre-build
priority: P0
---
```
Hi Ankit,

Look at Inkle's website, rebuild the tax application for an AI-first world for founders (use your imagination) with AI (Claude code/Antigravity/Codex), and send the results. Make sure to build both the frontend and the backend, send me a working video, code, and thought process. Also, think of how we will keep the human in the loop concept, as this is compliance.

Would love to chat
```
# 🧠 TaxOS — Full Context Document

> **One-liner:** An agentic, AI-first US tax & compliance platform for founders — where AI does 90% of the work, CPAs (Certified Public Accountant) or Chartered Institute of Management Accountants (CIMA) hold the pen on every submission, and founders never feel confused or blindsided.
![[Pasted image 20260403133214.png]]

---

## 📌 1. What Inkle Tax Does Today (Source Intelligence)

```yaml
inkle_tax:
  tagline: "Never miss another deadline again"
  core_promise: "Blends smart software with expert CPAs to simplify US tax compliance for startups"

  user_flow:
    step_1: "Enter company entity data (C Corp, state, jurisdiction(legal power or authority; the area in which this power can be used))"
        
    step_2: "Receive deadline alerts (AI-predicted, entity-aware)"
    step_3: "File Federal & State taxes (CPA-executed)"
    step_4: "Stay compliant year-round"

  key_features:
    - name: "Entity Management"
      detail: "Track domestic + foreign entities; AI autofills from history"
    - name: "Filing Tracker"
      detail: "Past, ongoing, upcoming filings in one view"
    - name: "Autofill"
      detail: "Prefills forms from prior filings and entity data"
    - name: "Filing Launcher"
      detail: "Launch filings in-platform; full document history   
        export const filingStatusEnum = pgEnum("filing_status", [
          "intake",           // AI collecting info
          "ai_prep",          // AI prefilling form
          "cpa_review",       // CPA reviewing draft
          "founder_approval", // Founder needs to sign off
          "submitted",        // Filed with IRS/state
          "archived"          // Done, stored for records
        ]);

    - name: "Deadline Alerts"
      detail: "Smart deadline engine — adjusts as entity details change"
    - name: "Inkle Chat"
      detail: "Built-in AI chatbot for tax/compliance Q&A"
    - name: "Document Vault"
      detail: "Secure centralized storage for all filings + docs"
    - name: "CPA Access"
      detail: "On-demand licensed CPAs"
    - name: "Compliance Dashboard"
      detail: "Federal + state level compliance status"

  supported_filings:
    federal:
      - Form 1120 (C Corp Income Tax)
      - Form 5471 (Foreign Corp Disclosure)
      - Form 5472 (Foreign-Owned US Corp)
      - Form 7004 (Extension)
      - Form 1099 (Contractor payments)
      - FBAR (Foreign Bank Accounts)
      - BOI (Beneficial Ownership Information)
      - 409A Valuation
    state:
      - Delaware Franchise Tax
      - Multi-state income tax
      - Sales tax (separate product)

  target_user: "US-incorporated startups, especially India-origin founders (Delaware C Corps)"
  business_model: "SaaS + CPA services (hybrid)"
  competitors: ["Pilot", "Clerky", "Stripe Atlas (partial)", "Gusto (payroll)", "TurboTax Business"]
  differentiator: "AI + CPA hybrid, founder-UX focused, India-to-US corridor expertise"
```

---

## 🚀 2. The Vision — TaxOS for an AI-First World

```yaml
taxos_vision:
  philosophy: >
    Tax compliance is not a product feature — it is existential for a startup.
    In an AI-first world, the founder should NEVER touch a tax form.
    The AI is the accountant. The CPA is the reviewer. The founder is the approver.
    Every action must be explainable, auditable, and reversible.

  design_principles:
    - "AI does, human approves — never the reverse"
    - "Zero ambiguity UX — every status is binary: done or needs attention"
    - "Proactive over reactive — surface deadlines 90 days out, not 9 days"
    - "Audit trail everything — every AI action has a reason log"
    - "Explain in plain English — no tax jargon without a tooltip"
    - "One-click escalation — founder can summon a CPA in < 60 seconds"

  north_star_metric: "Time founder spends on taxes per year < 2 hours"

  metaphor: >
    Like having a senior CPA + an AI paralegal working 24/7 on your behalf,
    surfacing only what genuinely needs your eyes.
```

---

## 🏗️ 3. Product Architecture

```yaml
product_architecture:
  name: TaxOS
  layers:

    data_layer:
      description: "Ingestion, normalization, storage of all financial signals"
      sources:
        - "Plaid / Mercury API (bank transactions)"
        - "QuickBooks / Xero integration (books)"
        - "Stripe (revenue events)"
        - "Manual document uploads (PDFs, W9s, 1099s)"
        - "IRS / State agency calendars (deadline sync)"
      storage:
        - "PostgreSQL (structured entity + filing data)"
        - "S3 / R2 (document vault)"
        - "Vector DB (pgvector — for AI retrieval of past filings)"

    agent_layer:
      description: "AI agents that do the actual work"
      agents:

        deadline_agent:
          role: "Monitors all entity deadlines, computes urgency scores"
          triggers: ["Entity created", "Fiscal year change", "State registration change"]
          outputs: ["Alerts", "Timeline updates", "Risk flags"]
          human_gate: "None — fully autonomous notifications"

        intake_agent:
          role: "Interviews founder to collect filing inputs"
          method: "Conversational form — chat-style, not form-style"
          outputs: ["Structured JSON payload for each filing"]
          human_gate: "Founder reviews and confirms data before handoff to CPA"

        document_agent:
          role: "Reads, classifies, and extracts data from uploaded documents"
          supports: ["PDF tax forms", "Bank statements", "Contracts", "Cap tables"]
          outputs: ["Structured extracted fields", "Confidence scores per field"]
          human_gate: "Low confidence fields flagged for human review"

        form_prefill_agent:
          role: "Auto-populates IRS and state forms using extracted + historical data"
          outputs: ["Pre-filled draft forms (PDF + structured)"]
          human_gate: "CPA must review and approve before submission"

        audit_risk_agent:
          role: "Scans completed filings for anomalies, inconsistencies, audit triggers"
          outputs: ["Risk score", "Flagged line items with explanation"]
          human_gate: "Any high-risk flag requires CPA sign-off"

        tax_qa_agent:
          role: "Answers founder questions in plain English"
          grounding: "IRS publications + past filings + entity data (RAG)"
          outputs: ["Cited answers with confidence level"]
          human_gate: "High-stakes answers (e.g., penalty exposure) escalate to CPA"

        status_agent:
          role: "Tracks filing workflow state across all entities"
          outputs: ["Real-time status board", "Proactive updates"]
          human_gate: "None — informational"

    workflow_layer:
      description: "Orchestration of human + AI steps per filing type"
      filing_lifecycle:
        - stage: "Intake"
          actor: "AI (intake_agent)"
          human_touchpoint: "Founder confirms collected data"
        - stage: "Document Collection"
          actor: "AI (document_agent)"
          human_touchpoint: "Founder uploads docs; low-confidence extractions flagged"
        - stage: "Form Preparation"
          actor: "AI (form_prefill_agent)"
          human_touchpoint: "CPA reviews draft form — required gate"
        - stage: "Audit Risk Check"
          actor: "AI (audit_risk_agent)"
          human_touchpoint: "CPA reviews any risk flags before submission"
        - stage: "Founder Approval"
          actor: "Human (Founder)"
          human_touchpoint: "Founder e-signs or explicitly approves — ALWAYS required"
        - stage: "Submission"
          actor: "AI or CPA (depending on jurisdiction)"
          human_touchpoint: "CPA submits; AI logs confirmation + receipt"
        - stage: "Post-Filing"
          actor: "AI (status_agent)"
          human_touchpoint: "Founder notified; document stored; next deadline surfaced"

    ui_layer:
      description: "What the founder sees"
      views:
        - "Command Center — single dashboard, everything in one glance"
        - "Filing Room — per-filing chat thread with AI + CPA"
        - "Deadline Calendar — visual timeline, entity-aware"
        - "Document Vault — drag-drop upload, AI-auto-tagged"
        - "AI Tax Advisor — conversational Q&A, always-on"
        - "Approval Queue — items that need founder eyes right now"
        - "Audit Trail — log of every AI action with reasoning"
```

---

## 🧩 4. Human-in-the-Loop (HITL) Design — Compliance Edition

```yaml
hitl_framework:
  philosophy: >
    In regulated compliance, AI is the researcher and drafter.
    Humans are the signatories and final decision-makers.
    No AI action that carries legal weight proceeds without a human gate.

  gate_types:

    founder_gate:
      description: "Things only the founder can approve"
      examples:
        - "Confirming entity data before filing"
        - "E-signing any tax form"
        - "Approving any payment (tax owed)"
        - "Authorizing a CPA to act on their behalf"
      ux: "Approval Queue card with summary, AI reasoning, and one-tap approve/reject"

    cpa_gate:
      description: "Things a licensed CPA must review before submission"
      examples:
        - "All pre-filled federal forms"
        - "Any form with a high audit risk score"
        - "Amended returns"
        - "Forms involving foreign assets or transactions"
        - "Penalty abatement requests"
      ux: "CPA Review Panel — form diff view, AI notes, confidence scores, comment thread"

    escalation_gate:
      description: "AI self-reports uncertainty and hands off"
      triggers:
        - "Confidence score < 0.75 on any extracted field"
        - "Conflicting data between two sources"
        - "Novel entity structure not seen in training data"
        - "IRS rule change in last 6 months"
      ux: "Inline 'I'm not sure — let me get a CPA' card with explanation"

    audit_trail:
      description: "Every AI action is logged with timestamp, model version, inputs, outputs, and human decision"
      storage: "Immutable append-only log (compliance-grade)"
      access: "Founder + CPA always; exportable for IRS audit"

  confidence_ui:
    principle: "Every AI output shows a confidence indicator"
    levels:
      high: "✅ AI confident — CPA spot-check recommended"
      medium: "⚠️ AI uncertain — CPA review required"
      low: "🚨 AI unsure — CPA must verify before proceeding"

  override_policy:
    ai_can_never:
      - "Submit any form without human approval"
      - "Make payments on behalf of the company"
      - "Waive or override a CPA review gate"
      - "Delete or modify filed documents"
    founder_can_always:
      - "Pause any AI workflow"
      - "Request CPA takeover at any stage"
      - "Download full audit trail"
      - "Revoke AI access to any data source"
```

---

## 🛠️ 5. Tech Stack

```yaml
tech_stack:
  frontend:
    framework: "Next.js 14 (App Router)"
    styling: "Tailwind CSS + shadcn/ui"
    state: "Zustand + React Query"
    ai_ui: "Vercel AI SDK (streaming chat)"
    auth: "Clerk"
    forms: "React Hook Form + Zod"
    charts: "Recharts"

  backend:
    runtime: "Node.js (Hono or Express)"
    language: "TypeScript"
    orm: "Drizzle ORM"
    database: "PostgreSQL (Supabase)"
    vector_db: "pgvector (for RAG on past filings)"
    queue: "BullMQ + Redis (agent job queue)"
    storage: "Cloudflare R2 (document vault)"
    auth: "Clerk JWT verification"

  ai_layer:
    primary_model: "claude-sonnet-4-20250514 (via Anthropic API)"
    orchestration: "Custom agent loop (tool-use pattern)"
    rag_pipeline: "LangChain.js OR custom (embed → store → retrieve)"
    document_extraction: "Claude vision API (PDF form parsing)"
    embedding_model: "Voyage AI or OpenAI text-embedding-3-small"

  integrations:
    banking: "Plaid API"
    accounting: "QuickBooks API, Xero API"
    payments: "Stripe"
    esign: "DocuSign or Dropbox Sign API"
    email: "Resend"
    notifications: "Knock (multi-channel)"
    calendar_sync: "Google Calendar API"

  infrastructure:
    hosting: "Vercel (frontend) + Railway or Fly.io (backend)"
    ci_cd: "GitHub Actions"
    monitoring: "Sentry + PostHog"
    secrets: "Doppler"

  ai_development_tools:
    - "Claude Code (primary agent dev + code review)"
    - "Cursor (IDE)"
    - "Windsurf (pair programming flows)"
```

---

## 🗂️ 6. Build Plan — Phases

```yaml
build_phases:

  phase_0:
    name: "Foundation"
    duration: "Week 1"
    deliverables:
      - "Monorepo setup (Next.js + Hono API)"
      - "Auth (Clerk)"
      - "DB schema (entities, filings, deadlines, documents, audit_log)"
      - "Design system (shadcn + Tailwind tokens)"
      - "Seed data (10 sample entities, 5 filing types)"

  phase_1:
    name: "Core Product — Deadline + Filing Engine"
    duration: "Week 2-3"
    deliverables:
      - "Entity management CRUD"
      - "Deadline calculation engine (rule-based + AI layer)"
      - "Filing tracker UI (Kanban: Not Started → AI Prep → CPA Review → Founder Approval → Filed)"
      - "Document vault (upload → AI auto-tag → structured storage)"
      - "Basic compliance dashboard"

  phase_2:
    name: "AI Agents"
    duration: "Week 4-5"
    deliverables:
      - "Intake Agent (conversational form via Claude)"
      - "Document Extraction Agent (Claude vision → structured JSON)"
      - "Form Prefill Agent (JSON → IRS form fields)"
      - "AI Tax Q&A (RAG on IRS pubs + past filings)"
      - "Audit Risk Agent (anomaly scoring)"
      - "HITL approval queues (founder + CPA gates)"

  phase_3:
    name: "CPA Workflow + HITL Polish"
    duration: "Week 6"
    deliverables:
      - "CPA Review Panel (diff view + comment threads)"
      - "Confidence score UI on all AI outputs"
      - "Audit trail viewer (immutable log)"
      - "Escalation flows (AI → CPA handoff)"
      - "E-sign integration (Dropbox Sign)"

  phase_4:
    name: "Integrations + Launch Polish"
    duration: "Week 7-8"
    deliverables:
      - "Plaid bank connection"
      - "QuickBooks sync"
      - "Notification system (email + in-app)"
      - "Onboarding flow (intake interview → entity setup)"
      - "Demo video + landing page"
```

---

## 📐 7. Database Schema (High Level)

```yaml
db_schema:
  tables:

    organizations:
      - id (uuid)
      - name
      - created_at
      - plan (free | starter | pro)

    entities:
      - id (uuid)
      - org_id (fk)
      - legal_name
      - entity_type (C-Corp | LLC | S-Corp)
      - state_of_incorporation
      - ein
      - fiscal_year_end
      - foreign_subsidiaries (jsonb)
      - created_at

    deadlines:
      - id (uuid)
      - entity_id (fk)
      - form_type (1120 | 5471 | DFT | etc)
      - due_date
      - status (upcoming | overdue | filed | extended)
      - ai_predicted (bool)
      - urgency_score (0-100)

    filings:
      - id (uuid)
      - entity_id (fk)
      - deadline_id (fk)
      - form_type
      - status (intake | ai_prep | cpa_review | founder_approval | submitted | archived)
      - ai_confidence_score
      - cpa_assigned_id
      - founder_approved_at
      - submitted_at
      - filing_data (jsonb — structured form fields)

    documents:
      - id (uuid)
      - filing_id (fk)
      - org_id (fk)
      - file_name
      - storage_url
      - extracted_data (jsonb)
      - ai_tags (text[])
      - confidence_score
      - reviewed_by_human (bool)

    audit_log:
      - id (uuid)
      - org_id (fk)
      - filing_id (fk)
      - actor_type (ai | cpa | founder)
      - actor_id
      - action
      - reasoning (text — AI must explain every action)
      - inputs (jsonb)
      - outputs (jsonb)
      - model_version
      - created_at

    approval_queue:
      - id (uuid)
      - org_id (fk)
      - filing_id (fk)
      - queue_type (founder | cpa)
      - status (pending | approved | rejected | escalated)
      - summary (AI-generated plain English)
      - ai_recommendation
      - created_at
      - resolved_at
      - resolved_by
```

---

## 🎨 8. UX Principles — Founder-First

```yaml
ux_principles:
  design_philosophy: "The IRS is scary. The UI should not be."

  key_screens:

    command_center:
      description: "Single dashboard — everything at a glance"
      components:
        - "Urgency strip: items needing attention TODAY"
        - "Filing pipeline (kanban-style across all entities)"
        - "Next 3 deadlines (countdown clock)"
        - "AI activity feed ('Your 1120 was prefilled — CPA reviewing')"
        - "Approval queue badge (red dot if anything pending)"

    filing_room:
      description: "Per-filing workspace — like a chat thread"
      components:
        - "Timeline sidebar (each stage with timestamp)"
        - "AI conversation thread (intake, updates, Q&A)"
        - "Document panel (attached docs with extraction preview)"
        - "Form preview (prefilled draft — read-only until CPA approves)"
        - "Approval card (founder e-sign gate)"
        - "CPA notes (visible to founder)"

    ai_advisor:
      description: "Always-on tax Q&A — 'the CPA in your pocket'"
      components:
        - "Chat interface (streaming)"
        - "Source citations (IRS pubs, past filings)"
        - "Confidence badge on every answer"
        - "Escalate to CPA button"
        - "Save to filing context"

    approval_queue:
      description: "The 'inbox' for compliance decisions"
      components:
        - "Card per pending item"
        - "AI-written summary (< 3 sentences)"
        - "What AI did + why"
        - "What founder needs to decide"
        - "Approve / Reject / Ask AI / Get CPA buttons"

    audit_trail:
      description: "Full log of everything AI touched"
      filters:
        - "By filing"
        - "By actor (AI / CPA / Founder)"
        - "By date range"
      export: "CSV + PDF (IRS-ready)"
```

---

## 🔒 9. Compliance + Security

```yaml
compliance_security:
  data_handling:
    - "SOC 2 Type II ready architecture"
    - "AES-256 encryption at rest"
    - "TLS 1.3 in transit"
    - "Field-level encryption for EIN, SSN, bank data"
    - "PII isolation per org (row-level security in Postgres)"

  ai_guardrails:
    - "No AI training on customer filing data"
    - "Model outputs never cached beyond session without explicit logging"
    - "All agent actions rate-limited and logged"
    - "Prompt injection protection on document extraction"

  access_control:
    roles:
      - founder: "Full access to own org; approve/reject gates"
      - team_member: "View-only + can submit intake info"
      - cpa: "Review + annotate + submit; cannot delete"
      - admin: "Full platform access (internal)"
    principle: "Least privilege + explicit delegation"

  regulatory:
    - "IRS e-file provider requirements"
    - "State-level efiling compliance per jurisdiction"
    - "GLBA (financial data protection)"
    - "CCPA / GDPR (user data rights)"
```

---

## 📦 10. Deliverables for This Build

```yaml
deliverables:
  code:
    - "Frontend: Next.js app (full source)"
    - "Backend: Hono API (full source)"
    - "Agent layer: Claude tool-use orchestration"
    - "DB migrations: Drizzle schema + seeds"
    - "README with local setup instructions"

  demo:
    - "Screen recording (Loom): Founder onboarding → AI intake → form prefill → CPA gate → Founder approval → Filed"
    - "Covers HITL at every gate"
    - "Shows audit trail"
    - "Shows AI confidence UI"

  docs:
    - "This context document (Obsidian YAML)"
    - "API docs (auto-generated via Hono Swagger)"
    - "Agent design doc (tool definitions + reasoning patterns)"

  thought_process:
    - "Architecture decision log"
    - "HITL design rationale"
    - "AI agent prompt engineering notes"
    - "What Inkle does well + what we're pushing further"
```

---

## 💡 11. What We're Pushing Beyond Inkle

```yaml
inkle_gaps_we_solve:
  - gap: "Inkle uses chat as a support channel"
    our_approach: "Chat IS the filing workflow — intake, Q&A, status, approval all in one thread"

  - gap: "AI autofills forms but human still has to navigate menus"
    our_approach: "Zero-nav experience — AI surfaces the right action at the right time; founder never browses"

  - gap: "HITL is implicit (CPA reviews, then files)"
    our_approach: "HITL is explicit, visible, and auditable — every gate is a named step with reasoning shown to founder"

  - gap: "Compliance dashboard is status-only"
    our_approach: "Compliance dashboard is predictive — AI forecasts risk 90 days out based on entity changes"

  - gap: "Document vault is storage"
    our_approach: "Document vault is intelligent — every doc is auto-extracted, cross-referenced, and available to agents"

  - gap: "One AI chatbot for Q&A"
    our_approach: "Multi-agent system: each agent has a specific role, tools, and handoff protocol"
```

---

*Last updated: 2026-04-03 | Status: Pre-build planning | Owner: TaxOS Team*
