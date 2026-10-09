# CLISONIX — CMP/CML + AdSense Monetization Playbook
## Version 1.0 (Mars 2026)

---

## 1) Qëllimi Ekzekutiv

Ky dokument përcakton planin profesional për aktivizim dhe optimizim të monetizimit me AdSense, me fokus te:

- **CMP** (Consent Management Platform) korrekt për EEA/UK/CH.
- **CML** (Consent Management Layer) të integruar në aplikacion për kontroll teknik të script-eve.
- **Compliance-first operations** për të mbrojtur llogarinë dhe të ardhurat afatgjata.
- **Rritje të CPC/CPM/RPM** në mënyrë legjitime dhe të qëndrueshme.

### Objektivi Financiar

- Të rritet probabiliteti që klikimet të bien në intervalin **€0.01–€1.00** sa më shpesh.
- **Nuk garantohet** vlerë fikse për çdo klikim, sepse CPC varet nga ankandi i reklamuesve, gjeografia, sezonaliteti, cilësia e trafikut dhe intent-i i audiencës.

---

## 2) Parime të Panegociueshme

1. **Zero shkelje policy** (Google Publisher Policies, invalid traffic, deceptive UI).
2. **Zero manipulim klikimesh** (self-click, incentivized clicks, click exchange, traffic artificial).
3. **Privacy-by-design** (consent para ad personalization në juridiksione relevante).
4. **Data-driven vendimmarrje** (A/B test, eksperimente të kontrolluara, rollback i shpejtë).
5. **Revenue durability > short-term spikes**.

---

## 3) Fusha e Punës (Scope)

### Në scope

- Setup CMP + Consent Mode v2.
- Integrim CML në frontend për kontroll të script loading.
- Ad placement strategy për rritje viewability dhe UX.
- KPI framework: CPC, CTR, Page RPM, viewability, fill-rate.
- Risk controls: invalid traffic detection dhe incident response.

### Jashtë scope

- “Guarantee” e CPC fikse për çdo klikim.
- Taktika gray/black-hat monetizimi.
- Manipulim i ankandit ose i trafikut.

---

## 4) Terminologji Praktike

- **CMP**: Platformë për menaxhimin e consent-it (IAB TCF 2.2 i rekomanduar për EEA).
- **CML**: Shtresë logjike në kodin e aplikacionit që vendos kur lejohen script-et (analytics/ads).
- **Consent Mode v2**: Parametrat `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`.
- **CPC**: Cost per click.
- **CPM**: Cost per 1000 impressions.
- **Page RPM**: Të ardhura për 1000 page views.

---

## 5) Readiness Checklist (para launch)

## 5.1 AdSense Account Readiness

- [ ] Publisher ID aktiv.
- [ ] Adresë pagese e verifikuar.
- [ ] Numër telefoni i verifikuar.
- [ ] Website approval i përfunduar.
- [ ] Ads.txt i konfiguruar korrekt në domain.

## 5.2 Website Readiness

- [ ] Content origjinal, i vlefshëm dhe i mjaftueshëm.
- [ ] Navigim i qartë, pa layout mashtrues.
- [ ] Privacy Policy, Cookie Policy, Terms të publikuara.
- [ ] Contact/Impressum të qarta.
- [ ] Performance web e pranueshme (Core Web Vitals).

## 5.3 Compliance Readiness (EEA/UK/CH)

- [ ] CMP i certifikuar, banner funksional.
- [ ] Consent Mode v2 aktiv.
- [ ] Ad tags nuk ngarkohen para consent-it kur kërkohet.
- [ ] Consent log/audit trail i ruajtur.

---

## 6) Arkitektura e Zbatimit (CMP + CML)

## 6.1 Rrjedha e Vendimmarrjes

1. User hyn në faqe.
2. CML vendos default consent (`denied` për rajonet relevante).
3. CMP shfaq banner dhe mbledh zgjedhjen.
4. CML përditëson Consent Mode v2 sipas zgjedhjes.
5. Vetëm pas consent-it të vlefshëm ngarkohen script-et e ads/personalization.

## 6.2 Rregulla të ngarkimit të script-eve

- **Strict mode** për EEA: asnjë ad personalization pa consent.
- **Region-aware behavior** për juridiksione jo-EEA sipas policy-së së brendshme.
- **Fail-safe**: në rast dështimi CMP, default duhet të jetë më konservativ (privacy-safe).

## 6.3 Evente që duhen loguar

- `consent_banner_shown`
- `consent_accept_all`
- `consent_reject_all`
- `consent_custom_save`
- `ads_script_loaded`
- `ads_script_blocked_no_consent`

---

## 7) Strategjia e Ad Placement (Revenue + UX)

## 7.1 Parime të vendosjes

- 1 unit **above the fold** pa dëmtuar readability.
- 1–2 units **in-article** në seksione me attention të lartë.
- 1 unit në fund të artikullit për intent të lartë.
- Ad density e kontrolluar; shmang overloading.

## 7.2 Rregulla UX

- Asnjë element që i ngjan butonit “download” mashtrues.
- Distancë e mjaftueshme nga CTA kritike të produktit.
- CLS minimal (rezervo hapësirën e ad-it paraprakisht).
- Mobile-first layout me testim në breakpoint-et kryesore.

## 7.3 Eksperimentim

- A/B test vetëm **një variabël** për cikël (pozicion, format, density).
- Minimum 7 ditë ose minimum page views të mjaftueshme për konkluzion.
- Rollback automatik nëse bie RPM ose rritet bounce-rate mbi prag.

---

## 8) Strategjia për CPC më të Lartë (legjitime)

## 8.1 Trafik me intent komercial

- Fokus në tema me qëllim blerjeje/zgjidhjeje.
- Artikuj “comparison”, “best tools”, “cost”, “implementation guide”.
- Landing pages të qarta me matching të mirë mes keyword dhe përmbajtjes.

## 8.2 Gjeografi & segmentim

- Prioritet tregjeve me bid më të lartë (p.sh. DACH, US, UK) në mënyrë organike.
- Localized content për audienca me vlerë.

## 8.3 Cilësi trafiku

- SEO organik, newsletter, social me intent real.
- Shmang “cheap traffic sources” me quality të ulët.
- Monitoro engagement (time on page, scroll depth, return rate).

---

## 9) Anti-Invalid Traffic & Risk Controls

## 9.1 Kontrollet Teknike

- Bot filtering (UA heuristics + rate limiting + anomaly detection).
- Throttling për burst-e jonormale nga i njëjti IP/device fingerprint.
- Alert për CTR spikes jashtë baseline.

## 9.2 Kontrollet Operacionale

- Audit javor i source/medium/campaign.
- Review manual për pages me CTR jonormal.
- Bllokim/referrer exclude kur dyshohet traffic i pavlefshëm.

## 9.3 Incident Response

1. Identifiko faqet/sources problematike.
2. Ule përkohësisht ad density në segmentin e prekur.
3. Filtrim i source-ve të dyshimta.
4. Dokumento incidentin dhe masat.
5. Monitoro 7 ditë post-incident.

---

## 10) KPI Framework & Targets

## 10.1 KPI kryesore (ditore/javore)

- **CPC**
- **CTR**
- **Page RPM**
- **Viewability**
- **Fill Rate**
- **Bounce Rate**
- **Session Duration**

## 10.2 Target bands realiste (fazë fillestare)

- CTR: **0.8% – 2.5%** (varion sipas niche).
- Viewability: **> 60%** për placements kryesore.
- CPC band target: **€0.01 – €1.00** në mënyrë probabilistike, jo deterministic.
- Objektiv primar: **rritje e Page RPM** pa shkelje policy.

## 10.3 Formula monitorimi

- `Page RPM = (Estimated earnings / Page views) * 1000`
- `CTR = (Clicks / Impressions) * 100`
- `CPC = Earnings / Clicks`

---

## 11) Plan Ekzekutimi

## 11.1 24 Orët e Para (Go-Live Readiness)

- Finalizo profilin AdSense dhe website approval prerequisites.
- Aktivizo CMP + Consent Mode v2.
- Vendos 2–3 ad units bazë me layout stabil.
- Vendos dashboard KPI (daily snapshot).

## 11.2 7 Ditët e Para (Stabilizim)

- Vëzhgo CTR/CPC/RPM sipas page template.
- Largo placements me viewability të dobët.
- Fillo 1 eksperiment A/B.
- Verifiko quality e trafikut dhe anomali CTR.

## 11.3 30 Ditët e Para (Optimization Loop)

- Iterim javor i ad layout.
- Iterim editorial për topic-e me intent më të lartë.
- Fine-tune i density për mobile.
- Raport mujor: fitime, risk score, plan i muajit pasues.

---

## 12) Governance (RACI i thjeshtuar)

- **Owner (Business):** prioritetet e të ardhurave dhe risk appetite.
- **Tech Lead:** CMP/CML, implementim script governance.
- **Content Lead:** strategji editoriale me intent komercial.
- **Analytics Owner:** dashboard, eksperimente, raportim.
- **Compliance Owner:** policy checks dhe audit trail.

---

## 13) Deliverables të Detyrueshme

1. Dokumentim i plotë CMP/CML setup.
2. Matricë e consent states dhe sjelljes së script-eve.
3. Dashboard KPI (daily/weekly).
4. Runbook për incidentet e invalid traffic.
5. Raport 30-ditor me vendime të argumentuara.

---

## 14) Quality Gate para Scale-Up

Scale-up i trafikut dhe inventory bëhet vetëm kur:

- Nuk ka sinjale invalid traffic.
- Consent flow kalon testet funksionale.
- RPM trend është stabil për të paktën 2 javë.
- Nuk ka warning/policy notice kritike në AdSense.

---

## 15) Përfundim

Qasja profesionale është: **compliance + cilësi trafiku + eksperimente të disiplinuara**. Kjo qasje nuk premton numra artificialë, por ndërton rritje të qëndrueshme dhe mbron llogarinë afatgjatë.

---

## Appendix A — Daily Operational Checklist

- [ ] Kontrollo earnings, CPC, CTR, RPM.
- [ ] Kontrollo pages me performancë më të ulët dhe më të lartë.
- [ ] Kontrollo trafik jonormal (source/IP/spike).
- [ ] Verifiko funksionimin e banner-it CMP.
- [ ] Log-o vendimet operative të ditës.

## Appendix B — Weekly Review Checklist

- [ ] Krahaso performancën sipas templates/pages.
- [ ] Vendos fituesin e testit A/B dhe bëj rollout.
- [ ] Përcakto 3 tema të reja me intent komercial.
- [ ] Bëj risk review për invalid traffic.
- [ ] Përditëso planin e javës pasuese.
