# Developer Path – UltraWebThinking

Ky dokument udhëzon çdo zhvillues për të ngritur, konfiguruar dhe zgjeruar platformën UltraWebThinking.

---

## 1. Klonimi i projektit

```bash
git clone https://github.com/Web8kameleon-hub/ultrawebthinking
cd ultrawebthinking
```

## 2. Instalimi i varësive

Platforma përdor yarn, npm dhe pip për module të ndryshme.

```bash
yarn install --immutable
# ose
npm install
```

## 3. Ngritja e infrastrukturës (Docker)

```bash
docker-compose up -d
```

## 4. Nisja e platformës në dev mode

```bash
yarn dev
# ose
npm run dev
```

## 5. Konfigurimi i moduleve

- Kontrollo folderët: mesh/, agi/, ddos/, governance/, patterns/, utt/, ai/, agisheet/
- Çdo modul ka dokumentacionin e vet në /docs/ultraweb/ ose README të brendshëm.
- Për të aktivizuar/deaktivizuar module, përdor .env ose config/ sipas udhëzimeve të dokumentacionit.

## 6. Zgjerimi i ekosistemit

- Shto module të reja në folderët përkatës.
- Regjistro API-të dhe shembujt në registry.
- Për çdo modul të ri, krijo një dokumentim të shkurtër në /docs/ultraweb/.

## 7. Testim & CI

```bash
yarn test
# ose
npm test
```

## 8. Deployment

- Vercel: `vercel --prod`
- Docker: `docker-compose up --build -d`
- Kubernetes: `kubectl apply -f k8s/`

---

## Këshilla

- Lexo gjithmonë README.md dhe /docs/ultraweb/ për ndryshime të fundit.
- Bashkëpuno me komunitetin për module të reja.
- Raporto çështje dhe sugjerime në GitHub Issues.

---

© UltraWebThinking – 2025+ | Web8Kameleon
