#!/usr/bin/env python3
"""
LayoffTrends Site Updater — v2
Runs every 2 hours via cron.

IMPORTANT: This script NEVER regenerates the full homepage HTML.
It reads index.html as a template, injects live news into marked
placeholders, and writes it back. Your design is always preserved.
"""

import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

NEWS_API_KEY  = "080cc35148fe414fa1179b62a2d37639"
OUTPUT_PATH   = "/var/www/layofftrends.com/index.html"
TEMPLATE_PATH = "/var/www/layofftrends.com/index.template.html"

RSS_FEEDS = [
    "https://techcrunch.com/tag/layoffs/feed/",
    "https://www.theverge.com/rss/index.xml",
]

def fetch_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [warn] {url}: {e}")
        return ""

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def fetch_news():
    articles = []
    url = (
        "https://newsapi.org/v2/everything"
        "?q=layoffs+%22job+cuts%22+OR+%22workforce+reduction%22+OR+%22laid+off%22+OR+%22redundancies%22&domains=techcrunch.com,reuters.com,bloomberg.com,cnbc.com,theverge.com,businessinsider.com"
        "&language=en&sortBy=publishedAt&pageSize=8"
        f"&apiKey={NEWS_API_KEY}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "ok":
            for a in data.get("articles", [])[:8]:
                articles.append({
                    "title":     (a.get("title") or "")[:120],
                    "source":    a.get("source", {}).get("name", ""),
                    "url":       a.get("url", "#"),
                    "excerpt":   (a.get("description") or "")[:180],
                    "published": (a.get("publishedAt") or "")[:10],
                })
    except Exception as e:
        print(f"  [warn] NewsAPI: {e}")

    keywords = ["layoff", "job cut", "workforce", "redundan", "restruc", "eliminat"]
    for feed_url in RSS_FEEDS:
        raw = fetch_url(feed_url)
        if not raw:
            continue
        try:
            root  = ET.fromstring(raw)
            items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
            for item in items[:10]:
                def tag(t):
                    el = item.find(t)
                    return el.text.strip() if el is not None and el.text else ""
                title   = tag("title") or tag("{http://www.w3.org/2005/Atom}title")
                desc    = tag("description") or tag("{http://www.w3.org/2005/Atom}summary")
                link    = tag("link") or tag("{http://www.w3.org/2005/Atom}link")
                pubdate = tag("pubDate") or tag("{http://www.w3.org/2005/Atom}updated")
                if any(k in (title + desc).lower() for k in keywords):
                    articles.append({
                        "title":     title[:120],
                        "source":    feed_url.split("/")[2].replace("www.", ""),
                        "url":       link or "#",
                        "excerpt":   re.sub(r"<[^>]+>", "", desc)[:180],
                        "published": pubdate[:10] if pubdate else "",
                    })
        except Exception as e:
            print(f"  [warn] RSS: {e}")

    seen, unique = set(), []
    for a in articles:
        k = a["title"][:50].lower()
        if k and k not in seen:
            seen.add(k)
            unique.append(a)
    return unique[:6]

def build_news_html(articles):
    if not articles:
        return '<p style="color:var(--ink-muted);font-size:13px;">No recent articles found. Check back soon.</p>'
    html = ""
    for i, a in enumerate(articles, 1):
        html += f"""
        <a href="{esc(a['url'])}" target="_blank" rel="noopener" class="news-card">
          <div class="news-num">0{i}</div>
          <div>
            <div class="news-title">{esc(a['title'])}</div>
            <div class="news-meta">{esc(a['source'].upper())} · {esc(a['published'])}</div>
            <div class="news-excerpt">{esc(a['excerpt'])}</div>
          </div>
        </a>"""
    return html

def ensure_template():
    """
    On first run: save current index.html as template with placeholders inserted.
    Subsequent runs: template already exists, just use it.
    """
    tpl = Path(TEMPLATE_PATH)
    out = Path(OUTPUT_PATH)

    if tpl.exists():
        return True  # already set up

    if not out.exists():
        print("  ERROR: index.html not found. Deploy your homepage first, then run this script.")
        return False

    print("  First run — creating template from current index.html...")
    html = out.read_text(encoding="utf-8")

    # Insert news placeholders around the news-list content
    # We look for the id="news" section and wrap the news cards
    if "<!-- LIVE_NEWS_START -->" not in html:
        # Find the news-list div opening and add start placeholder
        html = html.replace(
            '<div class="news-list">',
            '<div class="news-list"><!-- LIVE_NEWS_START -->'
        )
        # Find a reliable closing pattern after the news cards
        # The news-list closes before the body-aside
        html = html.replace(
            '    </div>\n  </div>\n  <aside class="body-aside">',
            '<!-- LIVE_NEWS_END -->\n    </div>\n  </div>\n  <aside class="body-aside">'
        )

    tpl.write_text(html, encoding="utf-8")
    print(f"  Template saved → {TEMPLATE_PATH}")
    return True

def main():
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # Load live stats from scraper
    stats = {}
    try:
        import json as _json
        stats = _json.loads(Path('/var/www/layofftrends.com/data/live_stats.json').read_text())
    except Exception as e:
        print(f"  [warn] Could not load live stats: {e}")
    print(f"\n{'='*52}")
    print(f"LayoffTrends updater v2 — {updated} UTC")
    print('='*52)

    if not ensure_template():
        return

    print("  Fetching live news...")
    articles  = fetch_news()
    news_html = build_news_html(articles)
    print(f"  Got {len(articles)} articles")

    # Read template (design source of truth)
    html = Path(TEMPLATE_PATH).read_text(encoding="utf-8")

    # Inject live stats if available
    if stats:
        total     = stats.get('total', 218400)
        companies = stats.get('companies', 831)
        warn      = stats.get('warn_notices', 1247)
        daily     = stats.get('daily_rate', 858)
        total_k   = f"{total/1000:.1f}K"

        # Replace KPI values
        import re as _re
        html = _re.sub(r'(class="kpi-value"[^>]*>)[\d,\.]+K?(<)', lambda m: m.group(1) + (total_k if 'TOTAL' in html[max(0,html.index(m.group(0))-200):html.index(m.group(0))] else m.group(2).split('<')[0]) + m.group(2), html)

        # Replace headline number
        html = _re.sub(r'<h1 class="hero-headline[^"]*">[\d,]+<br>', f'<h1 class="hero-headline fade-in">{total:,}<br>', html)

        # Replace KPI strip values precisely
        html = html.replace(
            '<div class="kpi-value">218.4K</div>',
            f'<div class="kpi-value">{total_k}</div>'
        )
        html = html.replace(
            '<div class="kpi-value">1,247</div>',
            f'<div class="kpi-value">{warn:,}</div>'
        )
        html = html.replace(
            '<div class="kpi-value">831</div>',
            f'<div class="kpi-value">{companies:,}</div>'
        )
        print(f"  ✅ Live stats injected: {total:,} jobs, {companies} companies")

    # Inject news between placeholders
    if "<!-- LIVE_NEWS_START -->" in html and "<!-- LIVE_NEWS_END -->" in html:
        before = html.split("<!-- LIVE_NEWS_START -->")[0]
        after  = html.split("<!-- LIVE_NEWS_END -->")[1]
        html   = before + "<!-- LIVE_NEWS_START -->" + news_html + "<!-- LIVE_NEWS_END -->" + after
        print("  ✅ News cards injected")
    else:
        print("  [warn] News placeholders missing from template — news not updated")
        print("         Delete the template file to regenerate it: rm", TEMPLATE_PATH)

    # Update timestamp wherever it appears
    html = re.sub(
        r'Last updated: [\d\-: ]+ UTC',
        f'Last updated: {updated} UTC',
        html
    )

    # Write final output
    Path(OUTPUT_PATH).write_text(html, encoding="utf-8")
    print(f"  ✅ index.html written → {OUTPUT_PATH}")
    print(f"     Articles: {len(articles)}")
    print(f"     Updated:  {updated} UTC\n")

if __name__ == "__main__":
    main()
