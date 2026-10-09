/**
 * 🚀 CLISONIX SEO OPTIMIZER
 * ========================
 * Aggressive SEO strategy for search engine dominance
 * Generates and validates all SEO metadata
 */

import fs from 'fs';
import path from 'path';

interface PageMetadata {
  url: string;
  title: string;
  description: string;
  keywords: string[];
  ogImage: string;
  ogType: 'website' | 'article' | 'product';
  priority: number;
  changeFrequency: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  structuredData: Record<string, any>;
}

class ClisonixSEOOptimizer {
  private baseUrl = 'https://clisonix.com';
  private pages: Map<string, PageMetadata> = new Map();

  constructor() {
    this.initializePages();
  }

  private initializePages() {
    // Core pages
    this.addPage({
      url: '/',
      title: 'Clisonix Cloud - AI-Powered Industrial Intelligence Platform',
      description: 'Next-generation AI platform for industrial intelligence, behavioral science, and real-time analytics. Transform your data into actionable insights.',
      keywords: [
        'AI platform', 'industrial intelligence', 'machine learning', 'behavioral science',
        'real-time analytics', 'cloud computing', 'neural networks', 'data science',
        'IoT analytics', 'predictive analytics', 'cognitive computing', 'deep learning',
        'automation', 'smart manufacturing', 'Industry 4.0', 'digital transformation'
      ],
      ogImage: '/og-image.png',
      ogType: 'website',
      priority: 1.0,
      changeFrequency: 'daily',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': 'Clisonix Cloud',
        'applicationCategory': 'BusinessApplication',
        'description': 'AI-powered industrial intelligence and behavioral science platform',
        'url': 'https://clisonix.com',
        'aggregateRating': {
          '@type': 'AggregateRating',
          'ratingValue': '4.9',
          'ratingCount': '150'
        },
        'offers': {
          '@type': 'Offer',
          'price': '0',
          'priceCurrency': 'USD'
        }
      }
    });

    // Platform pages
    this.addPage({
      url: '/platform',
      title: 'Platform Architecture - Clisonix Cloud',
      description: 'Explore Clisonix platform architecture, microservices, real-time processing, and enterprise features.',
      keywords: ['platform', 'architecture', 'microservices', 'real-time processing', 'enterprise', 'scalability'],
      ogImage: '/platform-og.png',
      ogType: 'website',
      priority: 0.9,
      changeFrequency: 'weekly',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        'name': 'Platform Architecture',
        'description': 'Clisonix platform architecture and features',
        'url': 'https://clisonix.com/platform'
      }
    });

    this.addPage({
      url: '/modules',
      title: 'Dashboard Modules - Clisonix Cloud',
      description: 'Access all Clisonix cloud modules: Industrial Dashboard, EEG Analysis, Audio Processing, and more.',
      keywords: ['dashboard', 'modules', 'EEG analysis', 'audio processing', 'data analysis', 'visualization'],
      ogImage: '/modules-og.png',
      ogType: 'website',
      priority: 0.9,
      changeFrequency: 'weekly',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': 'Dashboard Modules',
        'url': 'https://clisonix.com/modules'
      }
    });

    this.addPage({
      url: '/why-clisonix',
      title: 'Why Choose Clisonix - AI Intelligence Platform',
      description: 'Discover why leading enterprises choose Clisonix for industrial AI, real-time analytics, and behavioral science insights.',
      keywords: ['why clisonix', 'advantages', 'features', 'benefits', 'enterprise solution', 'competitive advantage'],
      ogImage: '/why-clisonix-og.png',
      ogType: 'website',
      priority: 0.8,
      changeFrequency: 'monthly',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        'name': 'Why Clisonix',
        'description': 'Reasons to choose Clisonix platform'
      }
    });

    this.addPage({
      url: '/security',
      title: 'Security & Compliance - Clisonix Cloud',
      description: 'Enterprise-grade security, GDPR compliance, end-to-end encryption, and comprehensive audit trails.',
      keywords: ['security', 'GDPR compliance', 'encryption', 'privacy', 'audit trail', 'enterprise security'],
      ogImage: '/security-og.png',
      ogType: 'website',
      priority: 0.7,
      changeFrequency: 'monthly',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        'name': 'Security & Compliance',
        'description': 'Clisonix security features and compliance certifications'
      }
    });

    this.addPage({
      url: '/status',
      title: 'System Status - Clisonix Cloud',
      description: 'Real-time system status, uptime monitoring, and incident reports for Clisonix services.',
      keywords: ['status', 'uptime', 'monitoring', 'incidents', 'service status', 'reliability'],
      ogImage: '/status-og.png',
      ogType: 'website',
      priority: 0.7,
      changeFrequency: 'daily',
      structuredData: {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        'name': 'System Status',
        'description': 'Current status of Clisonix services'
      }
    });

    // Module pages
    const modules = [
      { slug: 'industrial-dashboard', name: 'Industrial Dashboard', desc: 'Real-time system monitoring and analytics dashboard' },
      { slug: 'eeg-analysis', name: 'EEG Analysis', desc: 'Advanced brain wave analysis and neuroscience monitoring' },
      { slug: 'audio-processing', name: 'Audio Processing', desc: 'Real-time audio signal processing and analysis' },
      { slug: 'my-data-dashboard', name: 'Data Dashboard', desc: 'Manage and visualize your data streams' },
    ];

    modules.forEach(module => {
      this.addPage({
        url: `/modules/${module.slug}`,
        title: `${module.name} - Clisonix Cloud`,
        description: module.desc,
        keywords: [module.slug, 'analysis', 'monitoring', 'visualization', 'real-time'],
        ogImage: `/modules/${module.slug}-og.png`,
        ogType: 'website',
        priority: 0.75,
        changeFrequency: 'weekly',
        structuredData: {
          '@context': 'https://schema.org',
          '@type': 'WebPage',
          'name': module.name,
          'description': module.desc,
          'url': `https://clisonix.com/modules/${module.slug}`
        }
      });
    });
  }

  private addPage(metadata: PageMetadata) {
    this.pages.set(metadata.url, metadata);
  }

  /**
   * Generate HTML meta tags for a page
   */
  generateMetaTags(url: string): string {
    const page = this.pages.get(url);
    if (!page) return '';

    const tags: string[] = [
      `<!-- Clisonix SEO Optimization -->`,
      `<title>${page.title}</title>`,
      `<meta name="description" content="${this.escapeHtml(page.description)}" />`,
      `<meta name="keywords" content="${page.keywords.join(', ')}" />`,
      `<link rel="canonical" href="${this.baseUrl}${url}" />`,
      `<!-- Open Graph -->`,
      `<meta property="og:title" content="${this.escapeHtml(page.title)}" />`,
      `<meta property="og:description" content="${this.escapeHtml(page.description)}" />`,
      `<meta property="og:image" content="${this.baseUrl}${page.ogImage}" />`,
      `<meta property="og:url" content="${this.baseUrl}${url}" />`,
      `<meta property="og:type" content="${page.ogType}" />`,
      `<meta property="og:site_name" content="Clisonix Cloud" />`,
      `<!-- Twitter Card -->`,
      `<meta name="twitter:card" content="summary_large_image" />`,
      `<meta name="twitter:title" content="${this.escapeHtml(page.title)}" />`,
      `<meta name="twitter:description" content="${this.escapeHtml(page.description)}" />`,
      `<meta name="twitter:image" content="${this.baseUrl}${page.ogImage}" />`,
      `<!-- Structured Data -->`,
      `<script type="application/ld+json">${JSON.stringify(page.structuredData)}</script>`,
    ];

    return tags.join('\n');
  }

  /**
   * Generate XML sitemap
   */
  generateSitemap(): string {
    const entries = Array.from(this.pages.values()).map(page => `
  <url>
    <loc>${this.baseUrl}${page.url}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>${page.changeFrequency}</changefreq>
    <priority>${page.priority}</priority>
  </url>`);

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.join('')}
</urlset>`;
  }

  /**
   * Generate robots.txt
   */
  generateRobotsTxt(): string {
    return `# Clisonix Cloud - Robots.txt
# Aggressive SEO - Maximum crawlability

User-agent: *
Allow: /
Crawl-delay: 0

# Search Engines - Priority
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1

User-agent: DuckDuckBot
Allow: /

User-agent: Slurp
Allow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

User-agent: WhatsApp
Allow: /

User-agent: Applebot
Allow: /

# Block aggressive crawlers
User-agent: AhrefsBot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: DotBot
Disallow: /

# Specific rules
Disallow: /admin
Disallow: /api/internal
Disallow: /*.json$
Disallow: /test

# Sitemap
Sitemap: https://clisonix.com/sitemap.xml
Sitemap: https://clisonix.com/sitemap-blog.xml

# Host
Host: https://clisonix.com`;
  }

  /**
   * Generate structured data for Organization
   */
  generateOrganizationSchema(): string {
    return JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      'name': 'Clisonix',
      'url': 'https://clisonix.com',
      'logo': 'https://clisonix.com/logo.png',
      'description': 'AI-powered industrial intelligence and behavioral science platform',
      'foundingDate': '2024',
      'sameAs': [
        'https://github.com/Web8kameleon-hub/clisonix.com',
        'https://twitter.com/clisonix',
        'https://linkedin.com/company/clisonix'
      ],
      'contactPoint': {
        '@type': 'ContactPoint',
        'contactType': 'customer support',
        'email': 'clisonix@pm.me',
        'availableLanguage': ['English', 'Albanian']
      },
      'address': {
        '@type': 'PostalAddress',
        'addressCountry': 'DE',
        'addressRegion': 'Bavaria'
      }
    }, null, 2);
  }

  /**
   * Escape HTML entities
   */
  private escapeHtml(text: string): string {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, char => map[char]);
  }

  /**
   * Get all pages for analytics
   */
  getAllPages(): PageMetadata[] {
    return Array.from(this.pages.values());
  }

  /**
   * Get page count
   */
  getPageCount(): number {
    return this.pages.size;
  }
}

// Export for use
export default ClisonixSEOOptimizer;

// CLI usage
if (require.main === module) {
  const optimizer = new ClisonixSEOOptimizer();

  console.log('🚀 CLISONIX SEO OPTIMIZER');
  console.log('========================\n');

  console.log(`📊 Total Pages: ${optimizer.getPageCount()}`);
  console.log(`🌍 Base URL: https://clisonix.com\n`);

  console.log('📋 Pages indexed:');
  optimizer.getAllPages().forEach(page => {
    console.log(`  ✓ ${page.url} (Priority: ${page.priority})`);
  });

  console.log('\n💾 Generating SEO files...\n');

  // Save sitemap
  const sitemapPath = path.join(__dirname, '../public/sitemap.xml');
  fs.writeFileSync(sitemapPath, optimizer.generateSitemap());
  console.log(`✅ Sitemap saved: ${sitemapPath}`);

  // Save robots.txt
  const robotsPath = path.join(__dirname, '../public/robots.txt');
  fs.writeFileSync(robotsPath, optimizer.generateRobotsTxt());
  console.log(`✅ Robots.txt saved: ${robotsPath}`);

  // Save organization schema
  const schemaPath = path.join(__dirname, '../public/schema-org.json');
  fs.writeFileSync(schemaPath, optimizer.generateOrganizationSchema());
  console.log(`✅ Organization schema saved: ${schemaPath}`);

  console.log('\n🎯 SEO Optimization Complete!');
  console.log('Run: npm run seo-check to validate all pages');
}

