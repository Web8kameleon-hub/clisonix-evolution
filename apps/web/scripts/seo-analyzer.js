#!/usr/bin/env node

/**
 * 🔍 CLISONIX SEO ANALYZER & VALIDATOR
 * ====================================
 * Analyzes all pages for SEO best practices
 * Generates reports and recommendations
 */

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';

interface SEOReport {
  url: string;
  score: number;
  issues: string[];
  warnings: string[];
  recommendations: string[];
  metrics: {
    titleLength: number;
    descriptionLength: number;
    hasMetaDescription: boolean;
    hasCanonical: boolean;
    hasOgImage: boolean;
    hasStructuredData: boolean;
    hasH1: boolean;
  };
}

class SEOAnalyzer {
  private baseUrl = 'https://clisonix.com';
  private reports: SEOReport[] = [];

  constructor() {
    this.analyzePages();
  }

  async analyzePages() {
    const pages = [
      '/',
      '/modules',
      '/platform',
      '/why-clisonix',
      '/pricing',
      '/security',
      '/status',
      '/developers',
    ];

    console.log('🔍 CLISONIX SEO ANALYZER');
    console.log('=======================\n');
    console.log(`📊 Analyzing ${pages.length} pages...\n`);

    for (const page of pages) {
      const report = await this.analyzePage(page);
      this.reports.push(report);

      const statusIcon = report.score >= 80 ? '✅' : report.score >= 60 ? '⚠️' : '❌';
      console.log(`${statusIcon} ${page.padEnd(30)} Score: ${report.score}/100`);
    }

    this.generateReport();
  }

  private async analyzePage(page: string): Promise<SEOReport> {
    const url = `${this.baseUrl}${page}`;
    const report: SEOReport = {
      url: page,
      score: 0,
      issues: [],
      warnings: [],
      recommendations: [],
      metrics: {
        titleLength: 0,
        descriptionLength: 0,
        hasMetaDescription: false,
        hasCanonical: false,
        hasOgImage: false,
        hasStructuredData: false,
        hasH1: false,
      }
    };

    try {
      const response = await fetch(url, { timeout: 5000 });
      if (!response.ok) {
        report.issues.push(`HTTP ${response.status}: Page not accessible`);
        return report;
      }

      const html = await response.text();

      // Extract and analyze meta tags
      const titleMatch = html.match(/<title>(.*?)<\/title>/i);
      const descMatch = html.match(/<meta\s+name="description"\s+content="(.*?)"/i);
      const canonicalMatch = html.match(/<link\s+rel="canonical"\s+href="(.*?)"/i);
      const ogImageMatch = html.match(/<meta\s+property="og:image"\s+content="(.*?)"/i);
      const h1Match = html.match(/<h1[^>]*>(.*?)<\/h1>/i);
      const structuredDataMatch = html.match(/<script\s+type="application\/ld\+json">/i);

      // Validate metrics
      if (titleMatch) {
        report.metrics.titleLength = titleMatch[1].length;
        if (titleMatch[1].length < 30) {
          report.warnings.push('Title too short (< 30 characters)');
        } else if (titleMatch[1].length > 60) {
          report.warnings.push('Title too long (> 60 characters)');
        }
      } else {
        report.issues.push('Missing page title');
      }

      if (descMatch) {
        report.metrics.hasMetaDescription = true;
        report.metrics.descriptionLength = descMatch[1].length;
        if (descMatch[1].length < 120) {
          report.warnings.push('Meta description too short (< 120 characters)');
        } else if (descMatch[1].length > 160) {
          report.warnings.push('Meta description too long (> 160 characters)');
        }
      } else {
        report.issues.push('Missing meta description');
      }

      report.metrics.hasCanonical = !!canonicalMatch;
      if (!canonicalMatch) {
        report.warnings.push('Missing canonical tag');
      }

      report.metrics.hasOgImage = !!ogImageMatch;
      if (!ogImageMatch) {
        report.warnings.push('Missing Open Graph image');
      }

      report.metrics.hasStructuredData = !!structuredDataMatch;
      if (!structuredDataMatch) {
        report.recommendations.push('Add structured data (schema.org) markup');
      }

      report.metrics.hasH1 = !!h1Match;
      if (!h1Match) {
        report.issues.push('Missing H1 heading');
      }

      // Calculate score
      report.score = this.calculateScore(report);

    } catch (error) {
      report.issues.push(`Error fetching page: ${error}`);
      report.score = 0;
    }

    return report;
  }

  private calculateScore(report: SEOReport): number {
    let score = 100;

    // Deduct points for issues
    score -= report.issues.length * 15;

    // Deduct points for warnings
    score -= report.warnings.length * 5;

    // Add points for good practices
    if (report.metrics.hasCanonical) score += 5;
    if (report.metrics.hasOgImage) score += 5;
    if (report.metrics.hasStructuredData) score += 10;
    if (report.metrics.hasH1) score += 5;

    return Math.max(0, Math.min(100, score));
  }

  private generateReport() {
    const timestamp = new Date().toISOString();
    const averageScore = this.reports.reduce((sum, r) => sum + r.score, 0) / this.reports.length;

    const report = {
      timestamp,
      averageScore: Math.round(averageScore),
      totalPages: this.reports.length,
      pagesAbove80: this.reports.filter(r => r.score >= 80).length,
      pagesAbove60: this.reports.filter(r => r.score >= 60).length,
      totalIssues: this.reports.reduce((sum, r) => sum + r.issues.length, 0),
      totalWarnings: this.reports.reduce((sum, r) => sum + r.warnings.length, 0),
      pages: this.reports
    };

    // Save report
    const reportPath = path.join(__dirname, `../../public/seo-report-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    // Display summary
    console.log('\n📊 SEO ANALYSIS SUMMARY');
    console.log('======================');
    console.log(`Average Score: ${report.averageScore}/100`);
    console.log(`✅ Pages with 80+ score: ${report.pagesAbove80}/${report.totalPages}`);
    console.log(`⚠️  Pages with 60+ score: ${report.pagesAbove60}/${report.totalPages}`);
    console.log(`\n🚨 Total Issues: ${report.totalIssues}`);
    console.log(`⚠️  Total Warnings: ${report.totalWarnings}`);

    console.log(`\n📄 Full report saved to: ${reportPath}`);
    console.log(`🎯 Run this regularly to monitor SEO health!\n`);
  }
}

// Run analyzer
if (require.main === module) {
  new SEOAnalyzer();
}
