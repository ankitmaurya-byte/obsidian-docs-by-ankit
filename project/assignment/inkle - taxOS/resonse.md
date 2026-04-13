# IRS E-Filing Integration for TaxOS

## The Hard Truth First

The IRS does **not** offer a public REST API. To file electronically you must either:

1. **Become an IRS Authorized e-file Provider** — get an EFIN (Electronic Filing Identification Number), requires IRS application, background checks, and annual renewal
2. **Partner with an existing Authorized Provider** who exposes an API — much more practical for a startup

---

## Realistic Integration Paths

### Path 1 — Third-party Tax Filing API (Recommended for now)

Several companies already hold IRS authorization and expose REST/SOAP APIs.

| Provider | What it covers | Notes |
|---|---|---|
| **Sovos** | Federal + multi-state e-filing | Enterprise-grade, used by large filers |
| **TaxHero / TaxBandits** | 1099s, W-2s, business returns | REST API, startup-friendly |
| **Thomson Reuters ONESOURCE** | Corporate returns | Expensive, CPA-focused |
| **Nelco / Greatland** | 1099/W-2 filing | Simpler forms only |

For TaxOS (startup-focused, C-Corps/LLCs), **TaxBandits** has the most approachable API for business returns.

---

### Path 2 — IRS MeF Direct (Long-term, if you want full control)

The IRS MeF system uses **SOAP/XML over HTTPS**.

#### Data Flow

```
TaxOS backend
    │
    ▼
MeF XML Generator  ←── filing data from DB
    │
    ▼
IRS MeF Endpoint   (requires EFIN + IRS certification)
    │
    ▼
Acknowledgment file (ack) → update filing status
```

#### New Files to Build

```
apps/api/src/
├── integrations/
│   ├── mef/
│   │   ├── xml-builder.ts       # Build IRS XML from filing data
│   │   ├── mef-client.ts        # SOAP client to IRS endpoint
│   │   ├── ack-parser.ts        # Parse IRS acknowledgment response
│   │   └── schemas/             # IRS XML schemas per form type
│   │       ├── 1120.xsd
│   │       ├── 1065.xsd
│   │       └── 1120-S.xsd
│   └── eftps/
│       └── eftps-client.ts      # Tax payment via EFTPS
```

#### IRS XML Schema Example (Form 1120)

```xml
<Return xmlns="..." returnVersion="2023v4.0">
  <ReturnHeader>
    <ReturnTs>2024-04-15T10:00:00</ReturnTs>
    <TaxYr>2023</TaxYr>
    <Filer>
      <EIN>12-3456789</EIN>
      <BusinessNameLine1Txt>Acme Corp</BusinessNameLine1Txt>
    </Filer>
  </ReturnHeader>
  <ReturnData>
    <IRS1120>
      <TotalRevenueAmt>...</TotalRevenueAmt>
      ...
    </IRS1120>
  </ReturnData>
</Return>
```

TaxOS already stores `prefilled` JSON in the `filings` table — that data maps directly to these XML fields.

---

### Path 3 — Easiest Short-term: Generate IRS-ready PDF/XML for ExportIntake Conversation

Without any IRS authorization, TaxOS can:

1. Take the `prefilled` filing data
2. Map it to the official IRS form fields
3. Export a filled PDF (using a library like `pdf-lib`) or MeF-ready XML
4. The CPA downloads it and uploads to their authorized filing software

This requires zero IRS registration and can ship fast.

---

## What Changes in TaxOS's Filing Workflow

### Current Flow

```
... → founder_approval → submitted → archived
                              ↑
                    (manual, outside app)
```

### Future Flow

```
... → founder_approval → e_filing → ack_pending → submitted → archived
                              ↑             ↑
                        API call to     IRS sends
                        MeF/TaxBandits  acknowledgment
```

### New Filing Statuses

Extend the `status` enum in `apps/api/src/db/schema.ts`:

```typescript
['intake', 'ai_prep', 'cpa_review', 'founder_approval',
 'e_filing', 'ack_pending', 'submitted', 'rejected_by_irs', 'archived']
```

### New DB Table — Filing Submissions

Add to `apps/api/src/db/schema.ts` to track submission receipts:

```typescript
export const filingSubmissions = sqliteTable('filing_submissions', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  filingId: text('filing_id').references(() => filings.id),
  provider: text('provider'),           // 'mef' | 'taxbandits' | 'manual'
  submissionId: text('submission_id'),  // IRS or provider's reference ID
  acknowledgmentCode: text('ack_code'), // 'A' = accepted, 'R' = rejected
  acknowledgmentAt: text('ack_at'),
  rejectionReasons: text('rejection_reasons', { mode: 'json' }),
  createdAt: text('created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
})
```

---

## Practical Roadmap

| Timeline | Action |
|---|---|
| **Now** | Add PDF export of prefilled forms — CPA uploads to their software |
| **3–6 months** | Integrate TaxBandits API for 1099/W-2 (simpler forms first) |
| **6–12 months** | Apply for IRS EFIN, build MeF integration for 1120/1065/1120-S |
| **12+ months** | Add EFTPS payment scheduling, state e-filing via Federal/State MeF |

---

## Key References

- [IRS MeF System Overview](https://www.irs.gov/e-file-providers/modernized-e-file-mef-internet-filing)
- [IRS Authorized e-file Provider Application](https://www.irs.gov/e-file-providers/become-an-authorized-e-file-provider)
- [TaxBandits API Docs](https://www.taxbandits.com/api-solution/)
- [EFTPS for Businesses](https://www.eftps.gov/eftps/)
- [IRS MeF XML Schemas](https://www.irs.gov/e-file-providers/mef-schemas-and-business-rules)
