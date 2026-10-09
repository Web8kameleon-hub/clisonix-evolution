#!/usr/bin/env python3
"""
Fetch Real Articles from GitHub and serve locally
Creates routes for each service (Blerina, Albana, etc.)
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO = "LedjanAhmati/clisonix-blog"
BRANCH = "main"

headers = {
    "Accept": "application/vnd.github.v3+json"
}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

# Cache for articles
articles_cache = []
last_fetch = None

def fetch_articles_from_github():
    """Fetch real articles from GitHub static folder"""
    global articles_cache, last_fetch

    # Cache for 5 minutes
    if last_fetch and (datetime.now() - last_fetch).seconds < 300:
        return articles_cache

    print("📚 Fetching real articles from GitHub...")
    url = f"https://api.github.com/repos/{REPO}/contents/static"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"❌ GitHub API error: {resp.status_code}")
            return []

        files = resp.json()
        articles = []

        for f in files:
            if f['name'].endswith('.html'):
                # Fetch file content
                content_resp = requests.get(f['download_url'], timeout=10)
                if content_resp.status_code == 200:
                    content = content_resp.text

                    # Extract metadata from filename
                    import re
                    match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.html', f['name'])
                    if match:
                        date_str = match.group(1)
                        title_slug = match.group(2)
                        title = title_slug.replace('-', ' ').title()

                        # Extract author from content if exists
                        author = "Clisonix"
                        if "DR. ALBANA" in content or "Dr. Albana" in content:
                            author = "DR. ALBANA"
                        elif "Blerina" in content:
                            author = "Blerina"

                        articles.append({
                            'filename': f['name'],
                            'title': title,
                            'date': date_str,
                            'author': author,
                            'content': content,
                            'url': f['download_url']
                        })

        articles.sort(key=lambda x: x['date'], reverse=True)
        articles_cache = articles
        last_fetch = datetime.now()

        print(f"✅ Fetched {len(articles)} real articles")
        return articles

    except Exception as e:
        print(f"❌ Error fetching articles: {e}")
        return []

def get_category(article):
    """Auto-categorize articles"""
    title = article['title'].lower()
    content = article.get('content', '').lower()

    if 'eeg' in title or 'brain' in title or 'neural' in title:
        return 'eeg'
    if 'audio' in title or 'speech' in title or 'sound' in title:
        return 'audio'
    if 'cardiac' in title or 'medical' in title or 'clinical' in title:
        return 'medical'
    if 'fda' in title or 'gdpr' in title or 'compliance' in title:
        return 'compliance'
    if 'industrial' in title or 'manufacturing' in title:
        return 'industrial'
    return 'ai'

@app.route('/')
def index():
    """Main blog index with real articles"""
    articles = fetch_articles_from_github()

    # Process articles with categories
    processed = []
    for a in articles:
        processed.append({
            **a,
            'category': get_category(a)
        })

    # Load template
    template_path = Path(__file__).parent / "blog_index_template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace placeholder with real data
    articles_json = json.dumps([{
        'filename': a['filename'],
        'title': a['title'],
        'date': a['date'],
        'author': a['author']
    } for a in processed], ensure_ascii=False)

    html = template.replace('__ARTICLES_DATA__', articles_json)
    return html

@app.route('/article/<filename>')
def article(filename):
    """Serve individual article"""
    articles = fetch_articles_from_github()

    for a in articles:
        if a['filename'] == filename:
            return a['content']

    return "Article not found", 404

@app.route('/api/articles')
def api_articles():
    """API endpoint for articles list"""
    articles = fetch_articles_from_github()
    return jsonify([{
        'filename': a['filename'],
        'title': a['title'],
        'date': a['date'],
        'author': a['author'],
        'category': get_category(a)
    } for a in articles])

@app.route('/api/article/<filename>')
def api_article(filename):
    """API endpoint for single article"""
    articles = fetch_articles_from_github()

    for a in articles:
        if a['filename'] == filename:
            return jsonify({
                'filename': a['filename'],
                'title': a['title'],
                'date': a['date'],
                'author': a['author'],
                'content': a['content'],
                'category': get_category(a)
            })

    return jsonify({'error': 'Article not found'}), 404

@app.route('/services/blerina')
def blerina_info():
    """Blerina service info"""
    return jsonify({
        'service': 'Blerina',
        'description': 'Gap Detection & Conceptual Reconstruction Engine',
        'status': 'active',
        'port': 8035,
        'capabilities': [
            'Document gap analysis',
            'Conceptual discontinuity detection',
            'Signal generation for Trinity/Ocean',
            'Domain knowledge integration'
        ],
        'articles': len([a for a in fetch_articles_from_github() if 'blerina' in a.get('author', '').lower()])
    })

@app.route('/services/albana')
def albana_info():
    """DR. ALBANA service info"""
    return jsonify({
        'service': 'DR. ALBANA v2.0',
        'description': 'Medical Content Generation & Publishing',
        'status': 'active',
        'port': 8040,
        'capabilities': [
            'Clinical article generation (cardiology, hepatology, endocrinology)',
            '5-8 articles/day, 3500-6000 words each',
            'GitHub Pages auto-publishing',
            'Ollama LLM integration (llama3.2:1b)'
        ],
        'articles': len([a for a in fetch_articles_from_github() if 'albana' in a.get('author', '').lower()])
    })

@app.route('/services/content-factory')
def content_factory_info():
    """Content Factory service info"""
    return jsonify({
        'service': 'Content Factory',
        'description': 'Quality-First Content Pipeline',
        'status': 'active',
        'port': 8005,
        'strategy': 'Pillar Strategy: 1 deep article + 4 supporting pieces/week',
        'quality_threshold': 0.85,
        'capabilities': [
            'Technical content generation',
            'Multi-platform publishing',
            'Real metrics integration',
            'Code example generation'
        ],
        'articles': len(fetch_articles_from_github())
    })

@app.route('/health')
def health():
    """Health check"""
    articles = fetch_articles_from_github()
    return jsonify({
        'status': 'healthy',
        'articles_count': len(articles),
        'last_fetch': last_fetch.isoformat() if last_fetch else None,
        'github_repo': REPO,
        'services': {
            'blerina': 'http://localhost:8035',
            'albana': 'http://localhost:8040',
            'content_factory': 'http://localhost:8005',
            'blog_publisher': 'http://localhost:8041'
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CLISONIX REAL BLOG SERVER")
    print("="*60)
    print("\n📍 Routes:")
    print("   - http://localhost:9999/                  (Blog Index)")
    print("   - http://localhost:9999/article/<file>    (Individual Article)")
    print("   - http://localhost:9999/api/articles      (Articles API)")
    print("   - http://localhost:9999/services/blerina  (Blerina Info)")
    print("   - http://localhost:9999/services/albana   (Albana Info)")
    print("   - http://localhost:9999/health            (Health Check)")
    print("\n🔗 Live Blog: https://ledjanahmati.github.io/clisonix-blog/")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=9999, debug=True)
