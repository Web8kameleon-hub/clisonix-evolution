# Clisonix Sellable V1 Spec

## Goal

Turn Clisonix from a broad platform into a clear, buyable product with measurable ROI in 30 days.

## Core Positioning

Clisonix helps teams generate business-ready reports (Excel, Word, PDF, PowerPoint) from real data sources and APIs using natural-language commands.

## Product Rule (Locked)

- No backend logic rewrite for V1 success track.
- Focus only on UI packaging, service presentation, and go-to-market clarity.

## ICP (Single Segment for First 30 Days)

- Primary ICP: consulting firms that prepare weekly/monthly client reports.
- Buyer: consultant lead / delivery manager / founder.
- Pain: manual report assembly from many sources, slow turnaround, inconsistent output quality.

## Product Surface (What We Sell)

1. Ocean Curiosity Chat

- Purpose: Natural-language command interface.
- User value: Ask for a report/output instead of building workflows manually.
- Fixed role in V1:
  - "Më jep rapport..."
  - "Krahaso X me Y..."
  - "Gjenero përmbledhje..."

1. Web Reader

- Purpose: Ingest and normalize web/doc/data inputs for reporting.
- User value: One pipeline to collect sources and prepare reportable data.
- Fixed role in V1:
  - Lexon URL ose dokument.
  - Nxjerr përmbledhje.
  - Përgatit materiale për raport.

1. Client-Friendly Dashboard

- Purpose: One command box + output selection.
- User commands example:
  - "Generate monthly KPI report in Excel for sales + ops."
  - "Create a 10-slide executive summary in PowerPoint for Q2."
  - "Export incident summary to PDF with charts."
- Output formats: Excel, Word, PDF, PowerPoint.

1. API Marketplace (Pay-per-use)

- Purpose: Monetize capabilities through API keys and usage billing.
- User value: Predictable cost and scalable usage.
- Placement rule:
  - Keep this as a technical page for advanced users.
  - Not part of first-time client journey.
  - No marketing-heavy copy in this page.

1. Public Page

- Purpose: Explain problem, result, price, and start trial/pilot.
- Messaging: No AGI/ASI claims. Only business outcomes.
- Language rule:
  - Primary language: English.
- Minimal content rule:
  - One simple sentence:
    - "Clisonix generates automated reports from public data and documents."
  - One screenshot.
  - One CTA button: "View Demo".

## V1 Packages

### Pilot (First Customer Offer)

- 0-99 EUR one-time onboarding pilot
- 1 real use case
- 1 live demo flow
- 1 report pack delivered (Excel + PDF by default)
- Goal: prove value, then upgrade to monthly plan

### Free

- 1,000 requests/day
- Basic report templates
- Community support

### Pro (29 EUR/month)

- 10,000 requests/day
- Full report generation endpoints
- Priority support

### Enterprise (99 EUR/month + custom)

- 50,000 requests/day baseline
- SLA + custom integrations
- Dedicated support

## API Contract (V1)

### Command and Jobs

- `POST /api/v1/commands/execute`
- `POST /api/v1/reports/jobs`
- `GET /api/v1/reports/jobs/{job_id}`
- `GET /api/v1/reports/jobs/{job_id}/download`

### Output-specific

- `POST /api/v1/reports/excel`
- `POST /api/v1/reports/word`
- `POST /api/v1/reports/pdf`
- `POST /api/v1/reports/pptx`

### Data Ingestion

- `POST /api/v1/reader/ingest-url`
- `POST /api/v1/reader/ingest-file`
- `GET /api/v1/reader/sources`

### Monetization and Keys

- `GET /api/v1/api-access/plans`
- `POST /api/v1/api-access/keys/create`
- `GET /api/v1/api-access/keys`
- `GET /api/v1/api-access/usage/{key_id}`
- `POST /api/v1/api-access/keys/{key_id}/revoke`

## Execution Model (Client-Side Batch / BYOC)

- Default enterprise mode: report analysis and document generation run on client infrastructure.
- Clisonix control plane does not process customer raw files in this mode.
- Clisonix stores only:
  - API key or token reference (encrypted at rest)
  - job metadata (status, duration, output type)
  - billing usage counters
- Clisonix does not store:
  - raw source documents
  - generated report content by default
  - customer dataset payloads

### Batch Flow (Client Server)

1. Client submits command from dashboard.
2. Clisonix creates job ticket and signs execution payload.
3. Client-side runner/agent pulls the job and executes locally.
4. Runner returns only summary metadata and optional signed result URL.
5. Dashboard shows job status and download link from client-hosted storage.

### Required Components

- `clisonix-runner` on client server (docker service).
- Outbound-only connection from client runner to Clisonix queue/control APIs.
- Optional local output storage (S3-compatible, file share, or client DB).

### Control APIs for Client Batch Mode

- `POST /api/v1/runner/enroll`
- `POST /api/v1/runner/heartbeat`
- `GET /api/v1/runner/jobs/next`
- `POST /api/v1/runner/jobs/{job_id}/start`
- `POST /api/v1/runner/jobs/{job_id}/complete`
- `POST /api/v1/runner/jobs/{job_id}/fail`

### Security and Retention

- Keys/tokens encrypted with server-side KMS.
- Per-client scoped credentials; no shared execution tokens.
- Signed short-lived job claims (JWT) for runner execution.
- Default retention policy:
  - metadata: 30-90 days
  - logs: minimal operational logs only
  - content retention: disabled unless client opts in

### Client Value Statement

- "Data stays on your server. Clisonix orchestrates and bills usage, while execution remains under your control."

## Dashboard UX Requirements

- Browser-style shell layout.
- Primary top tab: `Web Reader`.
- Small, clean quick-action button under the top bar: `Archive & Search`.
- Side panel action: `Ocean Curiosity Chat`.
- Web Reader first flow: "Ngarko -> Lexo -> Perdore".
- One visible command box in the Chat panel.
- One output selector with four format buttons: Excel/Word/PDF/PPT.
- Template selector with 3 defaults:
  - Sales Report Pack
  - Operations Weekly Brief
  - Research Summary Pack
- Job status timeline: queued, processing, complete, failed.
- Download panel with generated files and timestamps.
- Top-right app launcher exists as a square grid icon (multi-dot menu).
- Secondary services remain available inside app launcher, not in primary flow.
- First-time client view shows only result flow:
  - Input -> Command -> Download
- API details are hidden from first-time flow and visible only in technical/apps area.

## UI IA (V1 Locked)

1. Top Browser Bar

- Tabs:
  - `Web Reader` (default active)
  - `Dashboard` (reports/results)
  - `Public Page`

1b. Top-Right App Launcher

- Grid icon (Google-apps style) placed top-right.
- Opens advanced services menu:
  - `API Marketplace`
  - `API Keys`
  - `IoT / Pay-Per-Use`
  - additional expert modules
- UX intent: only users who explicitly open this menu continue to advanced features.

1. Main Work Area

- Default screen always opens `Web Reader`.
- Reader card includes:
  - URL/file input
  - summary preview
  - "Send to report" action

1. Secondary Action

- `Archive & Search` appears as a compact button below the main tab row.
- Purpose: quickly access past reads, summaries, and generated outputs.

1. Right Utility Rail

- `Ocean Curiosity Chat` is a slim but persistent panel/button on the side.
- Opens command drawer for natural-language actions without leaving reader context.

## KPI Targets (First 30 Days)

- Activation: 20 teams create at least one report.
- Conversion: 10% free-to-paid.
- Usage: >= 200 successful report jobs.
- Reliability: >= 98% successful job completion.
- Latency target: p95 command-to-job-start < 2s.
- Time to first report: < 2 minutes.

## Definition of Done (V1)

- User can submit one command and receive output in selected format.
- API key enforcement is active on paid endpoints.
- Usage tracking (daily/monthly) visible per key.
- Public pricing page is live with clear CTA.
- 3 template packs are available and documented.

## 14-Day Execution Plan

### Days 1-3

- Finalize command flow and report job APIs.
- Stabilize Excel/PDF/PPT/Word generators.

### Days 4-6

- Enforce API key plan limits and usage metering.
- Add billing hooks for pay-per-use.

### Days 7-9

- Ship client-friendly dashboard with command box + output selector.
- Add templates and file download UX.

### Days 10-12

- Launch public page with outcome-based messaging + pricing.
- Add trial/pilot onboarding flow.

### Days 13-14

- Run outreach to first 50 prospects.
- Book 5 demos and secure first paid pilot.

## Sales Copy (Use on Public Page)

- "Generate client-ready reports from real data in minutes, not days."
- "From one command to Excel, Word, PDF, or PowerPoint."
- "Pay only for usage, scale when needed."
- "Replace 5 hours of reporting with 1 command."
- Hero line: "Your data never leaves your system."
- Public one-liner: "Clisonix generates automated reports from public data and documents."

## First Sellable Use-Case Page (Required)

- Page name: `Weekly Operations Report - Automated`
- Must show only:
  - Input sources (sales + ops files/URLs)
  - Output files (Excel + PDF)
  - One real screenshot
  - CTA: `View Demo`

## Demo Flow (Locked)

1. User types: `Generate weekly ops report`.
2. User selects `PDF` (or Excel).
3. User downloads output.
4. Total demo time target: 20-30 seconds.

## Non-Goals (V1)

- No broad AGI/ASI narrative on landing page.
- No multi-ICP expansion before first paid pilot proof.
- No new complex modules without direct ROI impact.

## Risk Controls

- Keep strict "no fake data" behavior in outputs.
- Return explicit errors when sources are unavailable.
- Maintain real health/status checks for core dependencies.

## Ownership

- Product owner: define ICP, message, package boundaries.
- Engineering owner: command pipeline, output jobs, reliability.
- GTM owner: pricing page, outreach, pilot conversion.
