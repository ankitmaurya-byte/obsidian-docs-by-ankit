# Doubts
what time startups have to fill tax and all these

# info
inkle use posthog for analytic - end point (https://us.i.posthog.com/i/v0)
not redirecting to app.inkle if im loggedin 
# competetor
## list
### Pilot          → Bookkeeping + tax, human-heavy, expensive
```yaml
pilot:
  founded: 2017
  backed_by: Stripe, Index Ventures
  pricing: $499–$849/month (bookkeeping) + tax add-on
  
  what_they_do_well:
    - Clean books (QuickBooks-based)
    - Dedicated bookkeeper per client
    - Tax filing as an add-on service
    - Decent startup credibility (YC, a16z portfolio companies use them)
  
  how_they_work:
    - You connect your bank + Stripe
    - A human bookkeeper categorizes transactions monthly
    - At tax time, a CPA files your returns
    - You get a dashboard showing P&L, burn rate
  
  where_they_fall_short:
    - Expensive — $6k–$10k/year before tax filing fees
    - Human-first, not AI-first — bookkeeper does the work, AI is minimal
    - No proactive deadline engine — reactive, not predictive
    - No India-US corridor expertise
    - Generic startup focus, not India-origin founder specific
    - No conversational intake — still email/Slack based coordination
    - No HITL transparency — you don't see what the CPA is doing 
```

    
#### Clerky         → Legal formation + docs, not tax
```yaml
clerky:
  founded: 2013
  pricing: $2,000 one-time (incorporation) + per-document fees
  
  what_they_do_well:
    - Delaware C-Corp formation — fastest in the market
    - SAFE notes, board consents, equity docs — all templated
    - YC's recommended formation tool (huge credibility)
    - Clean document vault for legal docs
  
  where_they_fall_short:
    - STOPS at formation — no ongoing compliance
    - Zero tax filing capability
    - No deadline tracking
    - No CPA access
    - After they incorporate you, you're on your own for taxes
    
  what_founders_do_after_clerky:
    - Clerky → then scramble for a CPA at tax time
    - Clerky → then find Pilot or Inkle for ongoing compliance
    - This gap is exactly where TaxOS lives
```
Stripe Atlas   → Company formation only, stops there
#### Gusto          → Payroll + HR, not tax compliance
```yaml
gusto:
  founded: 2011
  pricing: $40/month base + $6/person
  
  what_they_do_well:
    - Payroll processing — best in class for small teams
    - W2s, payroll tax deposits (940, 941) — automated
    - Benefits (health insurance, 401k) administration
    - Contractor payments + 1099 generation
    - Clean UI, founder-friendly
  
  where_they_stop:
    - Payroll taxes only — not income tax, not entity-level compliance
    - No Form 1120, no 5471, no Delaware Franchise Tax
    - No CPA access
    - No deadline engine for corporate filings
    
  the_overlap_with_taxos:
    - 1099 generation (Gusto does this, TaxOS should import it)
    - Payroll data needed for 1120 (Gusto exports, TaxOS ingests)
    - W2s (Gusto handles, TaxOS references)
```
#### TurboTax Biz   → DIY tax software, no AI, no CPA
```yaml
turbotax_business:
  pricing: $170 one-time (desktop software)
  
  what_they_do_well:
    - Cheap
    - Covers most common federal forms
    - Step-by-step interview style UI
    - Brand trust (Intuit)
  
  where_they_fall_short:
    - DIY — founder does all the work
    - No CPA included
    - No AI (just decision trees)
    - No deadline tracking
    - No document vault
    - No state compliance beyond basic
    - Completely offline/desktop — no collaboration
    - Zero support for India-US complexity (5471, FBAR etc.)
    - No audit trail, no HITL
    - Built for a Main Street LLC, not a VC-backed C-Corp
```
## graph comparison



```
AI-powered
                        ↑
            TaxOS       |
                        |
    Inkle               |
                        |
←───────────────────────┼────────────────────────→
  Formation only        |              Full-stack
                        |
    Clerky    Atlas     |    Pilot (human-heavy)
                        |
                        |    TurboTax (DIY)
                        ↓
                    Human-powered
```


# The Core Gap TaxOS Fills
## Every competitor either:
Stops at formation (Atlas, Clerky)
Stops at payroll (Gusto)
Is human-heavy and expensive (Pilot)
Is DIY with no AI or CPA (TurboTax)
Is close but not AI-first (Inkle)