# SEO & Ads Readiness (Operational)

## Current Status

- **SEO foundation:** enabled (`app/sitemap.ts`, `public/robots.txt`, page-level `metadata` exports)
- **Ads integration:** backend proxy routes exist in `ultracom/app/routers/ads_enterprise.py`
- **Production ads readiness:** **partial** (requires upstream configuration)

## What is already in place

1. **Indexing primitives**
   - `public/robots.txt` allows crawling and declares sitemap.
   - `app/sitemap.ts` generates sitemap entries.

2. **Metadata primitives**
   - Root and page-level metadata are present in app routes (`export const metadata`).

3. **Ads API surface**
   - Ads endpoints: `/api/ads/health`, `/api/ads/campaigns`, `/api/ads/serve`, `/api/ads/revenue`.
   - Routing is implemented through upstream proxy for enterprise ad stack.

## Required to be fully ads-ready

Set these environment variables on production server:

```env
ADS_UPSTREAM_URL=https://<your-ads-service>
ADS_UPSTREAM_TOKEN=<secure-token>
ADS_TIMEOUT=20
```

Without `ADS_UPSTREAM_URL`, the ads router returns `503 configuration_error`.

## SEO checklist before go-live

- Use one canonical production domain in:
  - `app/sitemap.ts` (`baseUrl`)
  - `public/robots.txt` (`Sitemap:` URL)
- Ensure `metadataBase`, `openGraph`, and `twitter` are set in root layout metadata.
- Verify no `noindex` headers/meta in production.
- Submit sitemap in Google Search Console and Bing Webmaster Tools.

## Quick verification commands

```powershell
# sitemap should render XML
curl.exe http://127.0.0.1:3000/sitemap.xml

# robots should be reachable
curl.exe http://127.0.0.1:3000/robots.txt

# ads health route (if ultracom service is running)
curl.exe http://127.0.0.1:3000/api/ads/health
```
