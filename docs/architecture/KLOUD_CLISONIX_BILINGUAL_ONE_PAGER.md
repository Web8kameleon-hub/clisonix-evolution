# Kloud + Clisonix — Bilingual One-Pager

---

## 🇦🇱 Shqip

### Çfarë është

`Clisonix` dhe `Kloud` janë ndërtuar për të punuar së bashku, por jo si një kodbazë e vetme.

- **Clisonix** = produkti, UI/UX, AI workflows, enterprise APIs
- **Kloud** = runtime sovran, distributed fabric, secure state and coordination
- **kloud-bridge** = shtresa lidhëse mes tyre

### Çfarë kemi bërë deri tani

- krijuam `packages/nanogrid` si shtresë interop
- krijuam `scripts/sync-nanogrid-profile.ps1`
- krijuam `services/kloud_bridge` si microservice i izoluar
- shtuam modul/tab në frontend për `Kloud Bridge`
- hoqëm fake/demo values nga pamja e prodhimit

### Ku jemi tani

- arkitektura është vendosur ✅
- bridge është krijuar ✅
- frontend është gati ✅
- live upstream wiring është ende në konfigurim ⏳

### Hapi i ardhshëm

- lidhje reale me `KLOUD_UPSTREAM_URL`
- monitoring dhe restart policy
- ndarje më e qartë mes view-it të klientit dhe view-it admin

---

## 🇬🇧 English

### What it is

`Clisonix` and `Kloud` are designed to work together without becoming a single merged codebase.

- **Clisonix** = product layer, UX, AI workflows, enterprise APIs
- **Kloud** = sovereign runtime, distributed fabric, secure coordination layer
- **kloud-bridge** = the isolated contract layer between them

### What has been completed

- built `packages/nanogrid` as the interop layer
- created `scripts/sync-nanogrid-profile.ps1`
- created the isolated `services/kloud_bridge` microservice
- added a customer-facing `Kloud Bridge` frontend module
- removed fake/demo values from production-facing flows

### Current state

- architecture direction is decided ✅
- bridge exists ✅
- frontend exists ✅
- live upstream wiring is still pending ⏳

### Next step

- connect the real `KLOUD_UPSTREAM_URL`
- add monitoring and restart policy
- separate customer view from admin diagnostics more clearly

---

## Short Positioning Statement

**Clisonix is the intelligent application layer; Kloud is the sovereign infrastructure fabric behind it.**
