---
title: Filing Workflow - Actions Explained
tags: [tax, filing, ai, workflow, cpa]
---

# 📌 Filing Detail - Actions Explained

## 1. Start Intake Agent
- **What it does**: Launches an AI-powered conversational interview with the founder
- **Business purpose**:
  - Replaces complex tax forms with simple Q&A
  - AI asks plain English questions like:
    - "What was your total revenue this year?"
    - "Did you hire any contractors?"
  - Collects all required filing data
- **When visible**:
  - Only when no intake conversation has started

---

## 2. Run Prefill Agent
- **What it does**:
  - AI auto-fills tax form fields using:
    - Intake data
    - Uploaded documents
    - Entity information
- **Business purpose**:
  - Eliminates manual data entry
  - Provides:
    - Confidence scores
    - Source attribution  
      *(e.g., Revenue: $500K — source: P&L, confidence: 95%)*
  - CPAs verify instead of starting from scratch

---

## 3. Run Audit Risk
- **What it does**:
  - AI evaluates filing and assigns IRS audit risk score (0–100)
  - Flags suspicious items
- **Business purpose**:
  - Enables proactive risk management
  - If score > 60:
    - Mandatory CPA review required
  - Detects:
    - Unusual deductions
    - Mismatched values
    - IRS red flags

---

## 4. Status Action (Dynamic)
- **What it does**:
  - Moves filing to next workflow stage
- **Workflow stages**:


- **Business purpose**:
- Enforces compliance workflow
- Prevents skipping steps

---

## 5. Pause Workflow
- **What it does**:
- Freezes filing at current stage
- **Business purpose**:
- Used when:
  - Missing documents
  - IRS queries
  - Founder unavailable
- Helps manage workload during tax season

---

## 6. Escalate to CPA
- **What it does**:
- Flags filing for urgent CPA attention
- **Business purpose**:
- Handles complex scenarios:
  - International income
  - M&A activity
  - Special tax credits
- Moves filing to priority review queue

---

## 7. Approve & Submit (Founder Only)
- **What it does**:
- Final approval by founder
- Filing marked as "submitted"
- **Business purpose**:
- Human-in-the-loop (HITL) safeguard
- Founder is legal signatory
- **When visible**:
- Only in `founder_approval` stage

---

## 8. Reject Filing (Founder Only)
- **What it does**:
- Founder rejects filing with reason
- Sends back for corrections
- **Business purpose**:
- Ensures accuracy
- Example:
  - "Revenue number is wrong, Q4 adjustment missing"
- **When visible**:
- Only in `founder_approval` stage

---

# 🔄 Overall Business Flow

# TaxOS Overview

taxos:
  overview: |
    TaxOS is a tax preparation and workflow management platform.
    It handles everything before actual IRS submission.

  workflow:
    pipeline: intake → ai_prep → cpa_review → founder_approval → submitted → archived

    stages:
      intake:
        description: AI gathers financial data via chat

      ai_prep:
        description:
          - Prefills form fields
          - Runs audit risk scoring

      cpa_review:
        description: CPA reviews prefilled data

      founder_approval:
        description: Founder signs off

      submitted:
        description: Marked as "filed" inside TaxOS

      archived:
        description: Stored for future reference

# ------------------------

limitations:
  filing_support: false

  no_integrations:
    - IRS Modernized e-File (MeF)
    - IRS Direct Pay
    - State tax agency APIs

  tech_stack:
    - Express
    - SQLite
    - Gemini

# ------------------------

post_submission:
  what_happens: |
    After submission, TaxOS does NOT file taxes.
    The CPA or founder must complete filing externally.

  actions:
    - Upload to IRS-authorized e-file provider
    - Mail paper return to IRS
    - Use IRS Direct File (if eligible)

  tools_examples:
    - TurboTax Business
    - Drake
    - UltraTax

# ------------------------

responsibilities:
  taxos_handles:
    - Data collection
    - AI preparation
    - Audit risk scoring
    - CPA review workflow
    - Founder approval workflow

  taxos_does_not_handle:
    - IRS submission
    - Payments
    - Government integrations

# ------------------------

mental_model:
  taxos: "Preparation Office"
  irs_systems: "Filing Counter"

# ------------------------

future_scope:
  - IRS MeF integration
  - State filing integrations
  - Direct submission pipelines


# frontend
EntitiesPage frontend component is not used 

claimFilingReview in auth.ts in web not used anywhere
releaseFilingReview
assignCpaOrganization