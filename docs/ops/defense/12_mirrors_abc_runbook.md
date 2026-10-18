# 12 Mirrors A+B+C Defensive Runbook (Cloudflare + Hetzner + OS-CLX)

Ky runbook implementon nje model mbrojtes me 12 mirror endpoints ne menyre plotesisht defensive dhe ligjore.

## Scope

- A (Aggressive): `/mirror-a1` ... `/mirror-a4`
- B (Balanced): `/mirror-b1` ... `/mirror-b4`
- C (Stealth): `/mirror-c1` ... `/mirror-c4`

Qellimi:
- Filtrim i trafikut automatik para origin
- Izolim i trafikut dyshues ne kanale noise
- Zero logjike biznesi ne endpoints mirror

## 1) Cloudflare (Edge First)

Script:
- `scripts/security/cloudflare_apply_12_mirrors.ps1`

Dry run:

```powershell
. .\scripts\security\cloudflare_apply_12_mirrors.ps1
Invoke-CFApply12Mirrors -ZoneId '<ZONE_ID>' -ApiToken '<TOKEN>' -OfficeCidrs @('1.2.3.4/32') -BlockedAsns @('13335') -DryRun
```

Live apply:

```powershell
Invoke-CFApply12Mirrors -ZoneId '<ZONE_ID>' -ApiToken '<TOKEN>' -OfficeCidrs @('1.2.3.4/32') -BlockedAsns @('13335')
```

Aplikon:
- `security_level=high`
- `bot_fight_mode=on`
- tenton `super_bot_fight_mode=on` (kur plani e lejon)
- firewall rules per mirror paths, scanner paths, dhe lock admin
- baseline burst rate limiting

## 2) Origin Lock (Hetzner)

Script:
- `scripts/hetzner/lock_origin_to_cloudflare.sh`

Dry run:

```bash
ADMIN_SSH_CIDR="203.0.113.10/32" bash scripts/hetzner/lock_origin_to_cloudflare.sh --dry-run
```

Live apply:

```bash
ADMIN_SSH_CIDR="203.0.113.10/32" bash scripts/hetzner/lock_origin_to_cloudflare.sh
```

Aplikon:
- lejon SSH nga CIDR i adminit
- lejon 80/443 vetem nga Cloudflare IP ranges
- mohon 80/443 direkt nga interneti

## 3) Nginx Mirror Endpoints (Noise Channel)

Konfigurimi ne origin duhet te kete endpoint-e mirror qe:
- nuk prekin DB, auth, billing, ose CLX core routes
- kthejne vetem payload statik
- kane rate/conn limits lokale

Skedari i prod-it tashme ka location block per `/mirror-a*`, `/mirror-b*`, `/mirror-c*` dhe limitohet ne 1 req/sec per IP me burst te vogel.

## 4) OS-CLX Routing Policy

Rekomandohet klasifikimi ne dy kanale:

- `public`: trafik real i klienteve
- `noise`: cdo kerkese ne `/mirror-*` ose e shenuar si dyshuese nga edge

Per `noise`:
- pa ekzekutim logjike biznesi
- pa akses DB
- vetem telemetri + response statik

## 5) Monitoring Checklist

- Cloudflare Security Analytics:
  - challenge/block events ne mirror paths
- Nginx access logs:
  - volum i `/mirror-*`
  - krahasim me trafik publik
- Origin CPU:
  - stabilizim pas aktivizimit te edge controls

## 6) Rollback

- Cloudflare: disable rules me tag `CLX-12MIRRORS`
- Origin firewall: hiq rregullat e fundit UFW te 80/443 sipas `ufw status numbered`
- Nginx: komento/hiq mirror block dhe reload nginx
