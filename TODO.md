# TODO — SEO + Public API Documentation (Phase 1)

## Step 1: Repo audit (completed)
- [x] Identified backend entrypoints and existing API catalog page
- [x] Identified Nginx routing for /api/ and / 
- [x] Checked for existing robots/sitemap/structured data (none found)

## Step 2: Add SEO assets
- [x] Create `robots.txt` (clisonix.com root)
- [x] Create `sitemap.xml` (basic index + placeholders for future sitemap entries)
- [x] Add `security.txt` to `/.well-known/`


## Step 3: Improve API catalog for SEO
- [x] Add JSON-LD schema markup to `clisonix.com/public/api-catalog.html`
- [x] Add OpenGraph/Twitter meta tags (or ensure page includes them)
- [ ] Ensure endpoint listings are crawlable HTML (minimize dependency on runtime JS)


## Step 4: Expose public docs endpoint (backend)
- [ ] Add FastAPI endpoint `/api/public-docs/openapi.json` (proxy to existing OpenAPI or file)
- [ ] Add FastAPI endpoint `/api/public-docs` (HTML that renders endpoint list + links)

## Step 5: Nginx wiring
- [ ] Ensure `/robots.txt`, `/sitemap.xml`, `/.well-known/security.txt` are served by static hosting or proxied
- [ ] Ensure `/api/public-docs*` are reachable through Nginx

## Step 6: Verification
- [ ] curl checks: status codes + content-type for robots/sitemap/docs
- [ ] basic SEO checks: structured data present, canonical set, noindex where required

