# 📰 News Branch Guide (`news`)

Ky dokument përkufizon rregullat operative për branch-in `news`, mënyrën e punës për ndryshime në Newsroom, dhe kontrollin minimal CI për stabilitet.

## 1) Qëllimi i branch-it `news`

Branch-i `news` përdoret për:

- zhvillim dhe mirëmbajtje të shërbimeve të lajmeve;
- ndryshime në `services/newsroom/**`;
- dokumentim të lajmeve dhe publikimit;
- përgatitje release për publikim të kontrolluar në `main`.

Nuk përdoret për ndryshime të gjera në core services pa lidhje me newsroom.

## 2) Scope teknik

Ndryshimet e lejuara në `news` fokusohen te:

- `services/newsroom/**`
- `NEWSROOM_DEPLOYMENT.md`
- `NEWSROOM_90DAY_ROADMAP.md`
- `PROJECT_STATUS_REPORT.md` (vetëm seksionet për news)
- `docs/**` (kur lidhen direkt me newsroom/news pipeline)

Për ndryshime jashtë këtij scope, përdor branch tjetër sipas konventës (`feature/*`, `fix/*`, `docs/*`).

## 3) Workflow i rekomanduar i punës

### Krijimi i branch-it

```bash
git checkout main
git pull origin main
git checkout -b news
```

### Sinkronizimi periodik me `main`

```bash
git checkout news
git fetch origin
git rebase origin/main
```

Nëse preferohet merge strategji në ekip:

```bash
git merge origin/main
```

### Commit standard

Përdor Conventional Commits:

- `feat(newsroom): add new publisher adapter`
- `fix(newsroom): handle empty feeds gracefully`
- `docs(news): update newsroom deployment steps`

## 4) PR policy për `news` → `main`

Çdo PR duhet të ketë:

- përshkrim të qartë të impaktit;
- listë risk-esh (nëse prek publikimin automatik);
- checklist verifikimi;
- kalim të workflow-it `News Branch CI`.

Template i shkurtër për PR:

```md
## Summary
- 

## Changed Areas
- services/newsroom/
- docs/

## Risk
- [ ] Low
- [ ] Medium
- [ ] High

## Validation
- [ ] CI green
- [ ] Local smoke test done
- [ ] /health endpoint verified
```

## 5) Quality gates minimale

Për branch-in `news` aplikohen minimalisht:

- Python syntax check për `services/newsroom`;
- import check për `services/newsroom/main.py`;
- markdown check i thjeshtë (file bosh / header i munguar);
- artifact me rezultatet e kontrollit.

Këto gate ekzekutohen nga workflow:

- `.github/workflows/news-branch.yml`

## 6) Teste lokale para push

```bash
python -m py_compile services/newsroom/main.py
python -c "import runpy; runpy.run_path('services/newsroom/main.py')"
```

Opsionale (kur ka Docker changes):

```bash
docker compose up -d --build newsroom
curl http://localhost:9800/health
```

## 7) Rollback strategy

Nëse një merge nga `news` shkakton regresion:

1. identifiko commit-in problematik;
2. `git revert <commit_sha>` në `main`;
3. krijo hotfix branch për korrigjimin;
4. rihap PR nga `news` vetëm pasi CI dhe smoke tests të jenë green.

## 8) Security dhe secrets

- Mos hardcode API keys (`NEWSAPI_KEY`, `GNEWS_API_KEY`, etj.).
- Përdor vetëm environment variables / GitHub Secrets.
- Verifiko që `.env` të mos bëhet commit me vlera reale.

## 9) Definition of Done (DoD)

Një task në `news` konsiderohet i mbyllur kur:

- kodi është merged në `main` përmes PR;
- `News Branch CI` është green;
- docs janë përditësuar (nëse ka ndryshim behavior);
- endpoint-et kritike (`/health`, `/status` nëse ekziston) janë verifikuar.

## 10) Owner-ship e rekomanduar

- Primary owners: team që menaxhon `services/newsroom`.
- Required reviewer: të paktën 1 reviewer me kontekst deployment.
- Për ndryshime në publikim automatik, kërkohet reviewer shtesë.

## 11) Facebook Page Operations

Ky branch përfshin edhe menaxhimin e publikimeve për faqen Facebook `Clisonix.com`.

Standardi i menaxhimit dhe copy approved gjendet te:

- `docs/FACEBOOK_PAGE_CLISONIX.md`

Çdo ndryshim në tone-of-voice, post templates, ose setup të faqes duhet të dokumentohet aty.

## 12) Publication Laws (Detyruese)

Për çdo publikim në branch-in `news` duhet respektuar:

- `docs/PUBLICATION_LAWS_CLISONIX.md`

Ky dokument është gate policy për legal/editorial compliance para publikimit.

---

Ky dokument është baseline operative për branch-in `news` dhe duhet të përditësohet sa herë ndryshon pipeline-i i newsroom-it.
