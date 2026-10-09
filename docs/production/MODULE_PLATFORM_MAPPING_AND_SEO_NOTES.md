# Module Platform Mapping and SEO Hardening Notes

## Problem Addressed

- Module surfaces were not tied to a single canonical platform map.
- SEO routing and sitemap data could drift from real module inventory.

## Changes Introduced

### 1) Central Module-to-Platform Mapping

- Added centralized mapping file:
  - `apps/web/src/lib/modules/platform-map.ts`
- Includes:
  - module id
  - route
  - platform classification
  - backing service
  - indexable flag

### 2) Modules Dashboard Platform Awareness

- Updated modules dashboard to show per-module platform label derived from centralized map.
- File updated:
  - `apps/web/app/modules/page.tsx`

### 3) Sitemap Uses Canonical Mapping

- Replaced static hardcoded module slug list with map-derived indexable slugs.
- File updated:
  - `apps/web/app/sitemap.ts`

### 4) Robots Hardening for SEO Quality

- Allowed crawl for public content and static assets.
- Disallowed private/sensitive routes (api/admin/account/private module pages).
- File updated:
  - `apps/web/app/robots.ts`

## Why This Improves SEO

- Reduces sitemap drift and stale URLs.
- Keeps private routes out of index while preserving crawlability of public pages.
- Improves semantic clarity for module inventory and platform identity.

## Follow-up Recommendations

1. Add per-module `generateMetadata` for top public module pages using map data.
2. Add automated sitemap sanity check in CI.
3. Validate robots/sitemap in Google Search Console after deploy.
