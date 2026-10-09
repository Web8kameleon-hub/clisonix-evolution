# CLISONIX — Monetization Implementation Backlog
## CMP/CML + AdSense + Revenue Operations
## Version 1.0 (Mars 2026)

---

## 1) Qëllimi

Ky backlog e kthen playbook-un strategjik në punë konkrete implementimi për `apps/web`, me fokus në:

- compliance me Google AdSense dhe privacy requirements,
- stabilitet teknik të monetizimit,
- rritje graduale të RPM/CPC përmes optimizimit të ligjshëm,
- monitorim dhe reagim operacional.

Dokumenti lidhet drejtpërdrejt me komponentët aktualë të projektit.

---

## 2) Gjendja Aktuale e Vëzhguar

### Komponentë ekzistues relevantë

- Layout global me inject të AdSense script: [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- Komponent slot për AdSense: [apps/web/src/components/ads/AdSenseSlot.tsx](apps/web/src/components/ads/AdSenseSlot.tsx)
- Komponent consent/ad footer: [apps/web/src/components/ads/AdFooterSlot.tsx](apps/web/src/components/ads/AdFooterSlot.tsx)
- Ads.txt route: [apps/web/app/ads.txt/route.ts](apps/web/app/ads.txt/route.ts)
- Setup notes për env vars: [apps/web/README.md](apps/web/README.md)

### Gaps kryesore që duhen adresuar

1. **AdSense script ngarkohet globalisht në layout** edhe pa një Consent Mode v2 të implementuar plotësisht.
2. **Consent state** aktual bazohet vetëm në `localStorage`, jo në një model enterprise me kategori dhe rajon.
3. **Fallback te publisher ID default** duhet trajtuar me kujdes operacional që të shmanget varësia nga hardcoded defaults.
4. **Tracking i ads events** ekziston pjesërisht, por jo si dashboard KPI dhe jo si runbook invalid traffic.
5. **CMP formal** dhe audit trail i consent-it nuk janë të dokumentuara si sistem i plotë.

---

## 3) Prioritetet Ekzekutive

### P0 — Kritike para scale-up

- Consent governance korrekt
- Script loading policy-correct
- Ads.txt correctness
- Privacy/compliance pages review

### P1 — E rëndësishme për performance

- Placement optimization
- KPI instrumentation
- Revenue reporting
- Invalid traffic detection

### P2 — Scale & experimentation

- A/B testing framework për placements
- Editorial monetization loops
- Regional optimization

---

## 4) Workstreams

## Workstream A — Consent, CMP dhe CML

### Ticket A1 — Zëvendëso consent-in minimal me model kategorik

**Prioritet:** P0  
**Objektiv:** Të kalohet nga modeli `accepted/declined` në consent state më të detajuar.

**Files primare:**
- [apps/web/src/components/ads/AdFooterSlot.tsx](apps/web/src/components/ads/AdFooterSlot.tsx)
- [apps/web/src/components/ads/AdSenseSlot.tsx](apps/web/src/components/ads/AdSenseSlot.tsx)

**Acceptance criteria:**
- Consent state mbështet të paktën:
  - `necessary`
  - `analytics`
  - `ads`
  - `adPersonalization`
- Default state është privacy-safe.
- Consent mund të lexohet nga të gjithë komponentët relevantë në mënyrë të unifikuar.

### Ticket A2 — Implemento Consent Mode v2

**Prioritet:** P0  
**Objektiv:** Të kontrollohen qartë `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`.

**Files primare:**
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)

**Acceptance criteria:**
- Default consent vendoset para çdo tag-u reklamash.
- Update ndodh vetëm pas zgjedhjes së user-it.
- Ka dokumentim të sjelljes për accept/reject/customize.

### Ticket A3 — Introduce CMP vendor selection

**Prioritet:** P0  
**Objektiv:** Zgjedhja dhe integrimi i një CMP production-ready.

**Deliverables:**
- Vendor shortlist
- Vendim arkitekturor
- Checklist legal/compliance

**Acceptance criteria:**
- Banner i qartë, jo mashtrues.
- Mbështetje për EEA/UK/CH.
- Audit trail për consent.

---

## Workstream B — Ad Loading Governance

### Ticket B1 — Gate AdSense script loading by consent

**Prioritet:** P0  
**Objektiv:** Script-i global i AdSense të mos ngarkohet në mënyrë të pakushtëzuar.

**File primar:**
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)

**Acceptance criteria:**
- Në rajonet ku kërkohet consent, script-i i ads nuk ngarkohet pa status të vlefshëm.
- Ka fallback behavior të sigurt në rast dështimi CMP.
- Nuk ka regressions në hydration ose rendering.

### Ticket B2 — Centralize ad configuration

**Prioritet:** P1  
**Objektiv:** Të shmanget shpërndarja e logjikës së ads në shumë pika pa governance qendrore.

**Suggested outputs:**
- `src/lib/ads/config.ts`
- `src/lib/consent/state.ts`
- `src/lib/ads/policy.ts`

**Acceptance criteria:**
- Të gjitha slot-et marrin config nga një burim i vetëm.
- Publisher ID dhe slot IDs nuk varen nga defaults të fshehura.

### Ticket B3 — Hardening i publisher ID resolution

**Prioritet:** P1  
**Files primare:**
- [apps/web/app/layout.tsx](apps/web/app/layout.tsx)
- [apps/web/src/components/ads/AdSenseSlot.tsx](apps/web/src/components/ads/AdSenseSlot.tsx)
- [apps/web/app/ads.txt/route.ts](apps/web/app/ads.txt/route.ts)

**Acceptance criteria:**
- Environment-based configuration preferohet.
- Missing config jep warning të qartë në logs, jo sjellje të paqartë.
- `ads.txt` mbetet korrekt dhe i testueshëm.

---

## Workstream C — Placement Optimization

### Ticket C1 — Inventarizo slot-et ekzistuese dhe faqet me fitim potencial

**Prioritet:** P1

**Target areas:**
- homepage
- pricing page
- content/news pages
- docs/developer pages me engagement të lartë

**Acceptance criteria:**
- Hartohet matrica `page template -> allowed slots -> priority`.
- Për secilin template caktohet max density.

### Ticket C2 — Standard placements library

**Prioritet:** P1  
**Objektiv:** Krijo library placements standarde.

**Placements të rekomanduara:**
- top banner
- in-content block
- bottom/article exit slot
- optional sidebar only ku UX e lejon

**Acceptance criteria:**
- Çdo placement ka dimension/reserved space.
- Zero/low CLS impact.

### Ticket C3 — Mobile-first ad review

**Prioritet:** P1

**Acceptance criteria:**
- Nuk mbulohet content kritik.
- Sticky formats përdoren vetëm kur janë policy-safe.
- Scroll depth dhe bounce-rate nuk degradojnë ndjeshëm.

---

## Workstream D — Analytics, KPI dhe Reporting

### Ticket D1 — Event taxonomy për monetization

**Prioritet:** P1

**Evente minimale:**
- `consent_banner_shown`
- `consent_accept_all`
- `consent_reject_all`
- `ad_slot_requested`
- `ad_slot_rendered`
- `ad_impression_recorded`
- `ad_click_suspected`
- `ad_blocked_no_consent`

**Acceptance criteria:**
- Eventet kanë naming të qëndrueshëm.
- Përfshijnë route, slot, variant, viewport category.

### Ticket D2 — KPI dashboard ditor/javor

**Prioritet:** P1

**KPI:**
- CPC
- CTR
- Page RPM
- Impressions
- Viewability proxy
- Bounce rate
- Session duration

**Acceptance criteria:**
- Raport ditor i automatizuar.
- Review javor me action items.

### Ticket D3 — Revenue anomaly alerts

**Prioritet:** P1

**Acceptance criteria:**
- Alert kur CTR del jashtë bandës baseline.
- Alert kur një source krijon volum jo normal.
- Alert kur një placement humb RPM në mënyrë të fortë.

---

## Workstream E — Invalid Traffic Defense

### Ticket E1 — Basic anomaly rules

**Prioritet:** P1

**Acceptance criteria:**
- Zbulim i burst-eve nga i njëjti IP/referrer/UA.
- Shënjim i faqeve me CTR jo normal.
- Logging i mjaftueshëm për hetim.

### Ticket E2 — Incident response runbook

**Prioritet:** P1

**Acceptance criteria:**
- Ka procedurë të shkruar: detect, isolate, reduce density, block source, review.
- Ka owner të caktuar dhe SLA reagimi.

---

## Workstream F — Content & Revenue Growth

### Ticket F1 — Commercial intent content map

**Prioritet:** P2

**Objektiv:** Përcakto temat që historikisht mbështesin bids më të larta.

**Content types:**
- comparison pages
- implementation guides
- pricing/cost explainers
- enterprise use cases

### Ticket F2 — Regional SEO prioritization

**Prioritet:** P2

**Acceptance criteria:**
- Prioritet i audiencave me monetization potential më të lartë.
- Plan editorial me pages të lokalizuara ku ka kuptim.

---

## 5) 14-Day Delivery Plan

### Days 1–3

- A1, A2 discovery + design
- B1 assessment
- B3 configuration hardening plan

### Days 4–7

- Implementim consent state central
- Gating i script loading
- Event taxonomy + tracking bazë

### Days 8–10

- Placement inventory
- Homepage + content template review
- Dashboard skeleton

### Days 11–14

- Invalid traffic rules minimaliste
- Weekly review ritual
- Final QA + go/no-go memo

---

## 6) Go/No-Go Criteria

**GO vetëm nëse:**

- Consent flow është testuar në browser-e kryesore.
- Ads script nuk ngarkohet gabimisht para consent-it ku kërkohet.
- Ads.txt është korrekt në production.
- Nuk ka layout regressions kritike.
- KPI bazë mund të raportohen.

---

## 7) Vendime të Rekomanduara menjëherë

1. Të mos bëhet scale-up i inventory para përfundimit të Workstream A dhe B.
2. Të centralizohet logjika e consent-it përpara se të shtohen slot-e të reja.
3. Të shmanget varësia operative nga defaults të hardcoded për publisher ID.
4. Të krijohet raport javor monetization/compliance si standard.

---

## 8) Dokumentet e Lidhura

- [docs/MONETIZATION_CMP_CML_ADSENSE_PLAYBOOK.md](docs/MONETIZATION_CMP_CML_ADSENSE_PLAYBOOK.md)
- [MONETIZATION_SETUP_GUIDE.md](MONETIZATION_SETUP_GUIDE.md)
- [MONETIZATION_30DAY_PLAN.md](MONETIZATION_30DAY_PLAN.md)
- [apps/web/README.md](apps/web/README.md)
