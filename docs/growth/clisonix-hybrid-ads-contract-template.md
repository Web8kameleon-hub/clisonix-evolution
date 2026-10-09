# Clisonix Hybrid Performance Ads Agreement (Template)

## Founder-Led Default (No Investors)

Use these defaults if Clisonix is bootstrapped and cashflow-sensitive:

- Monthly base retainer cap: **€400-€900**
- Initial monthly ad spend cap: **€800-€2,500**
- Pilot length: **60 days** (can extend to 90 only if KPI trend is positive)
- Performance-heavy split target: **>=70% variable compensation, <=30% fixed**
- Mandatory stop-loss: pause campaigns if no SQL within first **14 days** after launch

## 1) Parties and Scope

This Agreement is between:

- **Client**: Clisonix ("Client")
- **Agency**: [Agency Legal Name] ("Agency")

**Scope**: Paid acquisition services for B2B SaaS growth (strategy, creative testing, campaign setup, optimization, reporting).

## 2) Pilot Term and Renewal

- **Pilot term**: 60-90 days from Effective Date (Founder default: 60 days).
- **Review checkpoints**: Day 30, Day 60, Day 90.
- After pilot, either party may continue month-to-month under written confirmation.

## 3) Commercial Model (Hybrid)

### 3.1 Base Retainer (Low Floor)

- Monthly base retainer: **€[X]** (Founder default target: **€400-€900**)
- Purpose: operational execution (campaign management, reporting, experimentation).

### 3.2 Performance Bonus (Primary Compensation)

Agency earns bonuses only on validated business outcomes:

1. **Qualified Demo Booked**: €[A] per approved demo
2. **SQL (Sales Qualified Lead)**: €[B] per approved SQL
3. **New Paid Subscription**: €[C] one-time per new paid customer
4. **Net New MRR Bonus**: [D]% of first-month net new MRR attributed to Agency

Founder-friendly starting defaults (replace placeholders if needed):

- Qualified Demo: **€20-€50**
- SQL: **€80-€180**
- New Paid Subscription: **€150-€450**
- Net New MRR Bonus: **8-15%** of first-month attributable MRR

> If two bonus layers apply to the same account, payout follows this order: Demo -> SQL -> Paid -> MRR (no double counting unless explicitly approved in writing).

## 4) KPI Definitions (Binding)

- **Qualified Demo**: Meeting booked and attended by ICP account matching agreed firmographic and role criteria.
- **SQL**: Lead accepted by Sales team in CRM with status `SQL` and reason code.
- **New Paid Subscription**: First successful payment by a new account not previously paying in the last 12 months.
- **Net New MRR**: Additional monthly recurring revenue from newly converted paid accounts attributable to Agency campaigns.

## 5) Attribution Rules

- Source of truth: **CRM + UTM tracking + ad platform IDs**.
- Required UTMs: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, optional `utm_term`.
- Attribution window: **[30/60] days** from first tracked click.
- Tie-break rule (recommended): last non-direct click unless parties define multi-touch split.

## 6) Exclusions and Invalid Events

No performance fee is due for:

- Spam/fraud/bot leads
- Duplicate leads/accounts
- Existing customer expansion (unless separately agreed)
- Events lacking minimum tracking evidence in CRM/UTM logs

## 7) Reporting and Transparency

Agency must provide weekly and monthly reports including:

- Spend by channel/campaign
- CPL (qualified), cost per SQL, cost per paid customer
- Conversion rates by funnel stage
- Revenue attribution and MRR impact
- Experiment log (what changed, why, expected effect, result)

## 8) Budget and Approval Controls

- Monthly ad spend cap: €[Cap] (Founder default start: **€800-€2,500**)
- Any change above [15]% requires Client written approval.
- New channel launches require prior written approval.
- Hard stop-loss: if spend reaches **40% of monthly cap** without first qualified signal (qualified demo/SQL), Client may pause immediately.

## 9) Data Ownership and Access

- All ad accounts, pixels, and analytics properties are Client-owned.
- Agency must work inside Client-owned assets whenever possible.
- Upon termination, Agency hands over full assets, naming conventions, and documentation within 5 business days.

## 10) Exit Clause (Mandatory)

During pilot and after pilot:

- Client may terminate with **14 days notice**.
- If KPI floor is not reached for [2] consecutive checkpoints, Client may terminate immediately without penalty.
- Founder protection: if Agency misses onboarding milestones by >7 days, Client may terminate immediately.

## 11) KPI Floor (Pilot)

By Day 90, target minimums (example placeholders):

- Cost per SQL <= €[target]
- At least [N] validated SQLs
- At least [M] net new paid customers
- Positive trend in payback period

Founder default KPI floor (recommended starter):

- Day 30: at least **4 SQL** or clear improving trend with validated ICP quality
- Day 60: at least **10 SQL** and minimum **2 paid customers**
- Cost per SQL target band: **€120-€300** (adjust by ACV)
- Payback expectation: <= **4 months** for self-funded mode

## 12) Payment Terms

- Retainer invoiced monthly in advance.
- Performance fees invoiced monthly in arrears.
- Performance invoices include event-level evidence and CRM IDs.
- Payment terms: Net [15/30].
- Founder default payment discipline: Net **30**, with right to dispute non-evidenced performance events.

## 13) Non-Solicit and Confidentiality

Standard mutual confidentiality and non-solicit terms apply for [12] months after termination.

## 14) Signatures

- Client Representative: __________________ Date: ______
- Agency Representative: ________________ Date: ______

---

## Appendix A: ICP Criteria (Example)

- Company size: [10-500 employees]
- Region: [EU/US]
- Industry: [AI, healthtech, SaaS, data]
- Role seniority: [Founder, CTO, Product, Ops]

## Appendix B: Required Tracking Fields

- CRM: lead_id, lifecycle_stage, SQL flag, owner, status reason
- UTM: source, medium, campaign, content, term
- Revenue: account_id, first_paid_date, MRR value, plan
