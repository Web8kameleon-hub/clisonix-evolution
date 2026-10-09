# Vercel Deploy Notes for `apps/web`

## Recommended setup
- **Frontend**: Vercel
- **Backend / APIs / reporting**: Hetzner
- **Kubernetes**: later, once production is stable

## Vercel project settings
- **Framework Preset**: `Next.js`
- **Root Directory**: `apps/web`
- **Install Command**: `npm install`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

## Required environment variables
Use `.env.vercel.example` as the source of truth.

Minimum values for a working frontend:
- `NEXT_PUBLIC_APP_URL`
- `NEXTAUTH_URL`
- `SITE_URL`
- `NEXT_PUBLIC_API_URL`
- `API_INTERNAL_URL`
- `REPORTING_INTERNAL_URL`
- `OCEAN_INTERNAL_URL`
- `AUTH_SECRET` or `NEXTAUTH_SECRET`

## Domain layout
Recommended production shape:
- `www.clisonix.com` → Vercel frontend
- Hetzner keeps the backend services and Docker workloads
- Frontend routes call the Hetzner APIs using the environment variables above

## Pricing
- **Hobby**: free for testing / personal use
- **Pro**: paid, better limits and team/commercial features

For Clisonix, you can start on **Hobby** for setup/testing and move to **Pro** when traffic and team workflows need it.
