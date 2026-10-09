# 📘 Clisonix Facebook Page Playbook

Ky dokument është baseline operacional për faqen Facebook `Clisonix.com` dhe përdoret nga ekipi i newsroom për menaxhim, publikim dhe verifikim cilësie.

## 1) Page Identity (Source of Truth)

- **Page Name**: Clisonix.com
- **Category**: News & Media Website
- **Website**: <https://clisonix.com>
- **Address**: Rr.Th.Kalefi & 11 Nentori, Elbasan, Albania, 5001
- **Phone**: +355 69 402 5305
- **Email**: <mailto:clisonix@pm.me>
- **Hours**: Always open

## 2) Approved Bio (EN)

Use this version as default page description:

> Clisonix is an international AI-assisted news and analysis platform focused on verified reporting, institutional standards, and ethical journalism. We deliver global insights across technology, economy, policy, innovation, and society.

Short version (for limited fields):

> Verified AI-assisted journalism across technology, economy, policy, innovation, and society.

## 3) Brand Voice & Editorial Rules

- factual dhe i verifikueshëm;
- i fuqishëm në formulim, por neutral në ton;
- pa clickbait;
- pa pretendime mjekësore/ligjore/financiare pa burim;
- transparencë kur artikulli është AI-assisted;
- CTA i qartë: lexo artikullin në `clisonix.com`.

## 4) Publishing Format (Facebook)

Template i rekomanduar për postime:

```txt
{HEADLINE}

{1-2 fjali përmbledhje me vlerë publike}

Read full analysis:
{URL}

#Clisonix #News #AIJournalism
```

Rregulla minimale:

- 1 link kryesor për postim;
- 1 headline i qartë;
- 3–5 hashtags max;
- mos posto pa thumbnail/cover image nëse është e mundur.

## 5) First 7-Day Content Plan

- **Day 1**: Welcome post + misioni editorial.
- **Day 2**: Technology analysis (high trust topic).
- **Day 3**: Economy/policy explainer.
- **Day 4**: Innovation spotlight.
- **Day 5**: Society/ethics analysis.
- **Day 6**: Weekly roundup me 3 links.
- **Day 7**: Community prompt (“Çfarë teme doni javën tjetër?”).

## 6) Pinned Post (Recommended)

```txt
Welcome to Clisonix.com.

We publish verified AI-assisted reporting and analysis on technology, economy, policy, innovation, and society.

Read the latest:
https://clisonix.com
```

## 7) Page Setup Checklist (Meta)

- [ ] Profile photo dhe cover photo të sinkronizuara me brand
- [ ] About text i përditësuar me versionin approved
- [ ] Contact fields të plota (phone, email, website, address)
- [ ] CTA button aktiv (`Learn More` → `https://clisonix.com`)
- [ ] Pinned post publikuar
- [ ] First 3 posts live

## 8) Newsroom Integration (Auto-publish)

Konfigurimi i service-it newsroom përdor:

- `FB_PAGE_ID`
- `FB_PAGE_TOKEN`

Ref: `services/newsroom/main.py` dhe `services/newsroom/.env`.

## 9) Safety & Compliance

- mos publiko credentials ose token në postime/screenshots;
- mos përdor materiale me copyright pa leje;
- verifiko link-et para publikimit;
- në rast gabimi editorial: korrigjim transparent + repost i qartë.

## 10) KPI javore (minimum)

- reach total;
- link clicks;
- engagement rate;
- follower growth;
- top 3 postime sipas CTR.

## 11) Daily Posting Cadence

Cadence default për faqen:

- `3 postime/ditë`

Cadence i zgjatur:

- `5 postime/ditë max`

Planifikimi operacional dhe copy i gatshëm gjendet te:

- `docs/FACEBOOK_DAILY_POSTING_PLAN.md`

## 12) Mandatory Publication Laws

Të gjitha postimet në Facebook duhet të jenë në përputhje me:

- `docs/PUBLICATION_LAWS_CLISONIX.md`

Në konflikt mes stilit të copy dhe rregullit ligjor/compliance, prioritet ka policy ligjore.

---

Owner: Newsroom/Media Team

