# Microservices Local Topology

Ky setup e ndan zhvillimin në shërbime të pavarura që shmangin konfliktet e porteve.

## Services

- `web` (Next.js): zgjedh automatikisht një port të lirë nga `3000,3001,3002,3010`
- `api` (Express backend): zgjedh automatikisht një port të lirë nga `8080,8081,8082,8090`
- `redis` (opsionale): `6379`
- `postgres` (opsionale): `5432`

## Run

```bash
yarn ultra
```

Script-i `scripts/dev-microservices.mjs`:

- përdor `127.0.0.1`
- kontrollon nëse porta është e lirë
- nis `web` dhe `api` me porta të ndara
- ndalon të dy shërbimet kur njëri bie

## Override port ranges

```bash
ULTRA_WEB_PORTS=3005,3006 ULTRA_API_PORTS=8090,8091 yarn ultra
```

## Legacy mode

Nëse do sjelljen e vjetër me porta fikse:

```bash
yarn ultra:legacy
```
