# 🔐 Google Search Console Setup Guide

> Step-by-step guide to maximize Clisonix visibility in Google Search

---

## Step 1: Verify Your Site

### Method A: HTML File (Recommended)

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Click "Add Property" → Select "URL prefix"
3. Enter: `https://clisonix.com`
4. Choose verification method: **HTML file**
5. Download the verification file
6. Place in: `apps/web/public/google[verification-code].html`
7. Click "Verify"

### Method B: HTML Tag (Alternative)

1. Copy the meta tag from GSC
2. Add to `apps/web/app/layout.tsx`:

```tsx
export const metadata: Metadata = {
  // ... other config
  verification: {
    google: 'YOUR_GOOGLE_VERIFICATION_CODE', // ← Add here
  },
}
```

---

## Step 2: Submit Sitemap

1. In Google Search Console
2. Left menu → **Sitemaps**
3. Enter: `https://clisonix.com/sitemap.xml`
4. Click **Submit**

**Monitor:**
- ✅ Sitemaps submitted
- ✅ Submitted URLs
- ✅ Indexed URLs
- ⚠️ Errors/warnings

---

## Step 3: Request Indexing

### For New Pages

1. Go to **URL Inspection** (top bar)
2. Enter page URL: `https://clisonix.com/modules`
3. Click **Request Indexing**
4. Google will crawl within 24-48 hours

### Bulk Request

Use the sitemap - Google will auto-discover all pages.

---

## Step 4: Monitor Performance

### Coverage Report

Shows which pages are indexed:

- **Excluded** - Pages Google chose not to index
- **Error** - Pages with crawl errors
- **Valid with warnings** - Indexed but has issues
- **Valid** - Fully indexed ✅

### Performance Report

Shows search visibility:

- **Clicks** - How many users clicked from search
- **Impressions** - How many times shown in results
- **CTR** - Click-through rate (target: 3-5%)
- **Average position** - Ranking position

---

## Step 5: Fix Common Issues

### Crawl Errors

**Solution:**
```
- Check server response (200 OK)
- Verify page is accessible
- Check robots.txt isn't blocking
- Fix internal links
```

### Index Coverage Issues

**Solution:**
```
- Add unique meta descriptions
- Create H1 tags
- Add structured data
- Improve content quality
```

### Manual Actions

**Solution:**
```
- Review Google penalty notice
- Fix violations
- Request reconsideration
```

---

## Step 6: Optimize Core Web Vitals

### Target Metrics

| Metric | Target | Current |
|--------|--------|---------|
| LCP (Largest Contentful Paint) | < 2.5s | ? |
| FID (First Input Delay) | < 100ms | ? |
| CLS (Cumulative Layout Shift) | < 0.1 | ? |

### Improvements

- ✅ Optimize images (WebP, lazy load)
- ✅ Minimize CSS/JS
- ✅ Use server-side rendering
- ✅ Enable compression
- ✅ Leverage browser caching

---

## Step 7: Schema.org Markup Validation

### Test Your Schema

1. Go to [Rich Results Test](https://search.google.com/test/rich-results)
2. Paste your URL or HTML
3. Check for ✅ valid structured data

**Expected Results:**
- ✅ Organization
- ✅ Software Application
- ✅ Breadcrumbs
- ✅ FAQs

---

## Step 8: Mobile Optimization

### Mobile-Friendly Test

1. Go to [Mobile-Friendly Test](https://search.google.com/mobile-friendly)
2. Enter: `https://clisonix.com`
3. Verify: ✅ Mobile friendly

**Clisonix Status:** ✅ Fully mobile-optimized

---

## Step 9: Security & HTTPS

### Requirements

- ✅ HTTPS enabled
- ✅ SSL certificate valid
- ✅ Mixed content warnings: 0

**Clisonix Status:** ✅ Fully secured

---

## Step 10: Submit to Other Search Engines

### Bing Webmaster Tools

1. Go to [Bing Webmaster](https://www.bing.com/webmaster)
2. Add site: `https://clisonix.com`
3. Verify with DNS or HTML file
4. Submit sitemap

### Yandex (for Russian market)

1. Go to [Yandex Webmaster](https://webmaster.yandex.com)
2. Add site
3. Verify and submit sitemap

---

## 📊 Monthly Monitoring Checklist

- [ ] Check GSC Performance Report
- [ ] Review Coverage for new errors
- [ ] Check Core Web Vitals scores
- [ ] Verify mobile usability
- [ ] Review top performing queries
- [ ] Check for security issues
- [ ] Review crawl statistics
- [ ] Update sitemap if pages added
- [ ] Check for manual actions
- [ ] Analyze competitor rankings

---

## 🎯 Target Keywords to Track

### High Priority

1. "AI platform" - Target position: #1-3
2. "Industrial intelligence" - Target: #1-5
3. "Machine learning platform" - Target: #1-10
4. "Behavioral science analytics" - Target: #1-5

### Medium Priority

5. "Real-time analytics platform"
6. "Cloud AI solutions"
7. "Neural networks platform"
8. "Data science cloud"

### Long-Tail

- "AI platform for industrial monitoring"
- "EEG analysis software"
- "Real-time audio processing"

---

## 📈 Expected Results Timeline

### Month 1
- ✅ Sitemap indexed
- ✅ Initial crawling
- ⏳ First rankings (3-10 position)

### Month 2-3
- ✅ Increased impressions
- ✅ 20-50 clicks/month
- ⏳ Rising positions

### Month 3-6
- ✅ 100-500 clicks/month
- ✅ Top 10 positions for main keywords
- ⏳ Backlink building

### Month 6+
- ✅ 1000+ clicks/month
- ✅ Top 3 positions for key terms
- ✅ Sustained organic traffic

---

## 🚀 Advanced Tactics

### 1. Content Marketing
- Blog posts (2-3/week)
- Target long-tail keywords
- Link to main service pages

### 2. Technical SEO
- Implement FAQ schema
- Breadcrumb schema
- Event schema (for webinars)

### 3. Link Building
- Guest posts on tech blogs
- Research citations
- Press releases
- Resource page links

### 4. User Experience
- Improve page speed
- Better mobile UX
- Reduce bounce rate
- Increase time on page

---

## 🔗 Useful Links

- [Google Search Console](https://search.google.com/search-console)
- [Rich Results Test](https://search.google.com/test/rich-results)
- [Mobile-Friendly Test](https://search.google.com/mobile-friendly)
- [Page Speed Insights](https://pagespeed.web.dev)
- [Google Analytics](https://analytics.google.com)
- [Schema.org Documentation](https://schema.org)

---

**📝 Setup Date: March 7, 2026**  
**🎯 Target: Rank #1 for primary keywords within 12 months**
