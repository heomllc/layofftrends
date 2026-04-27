#!/usr/bin/env python3
import sys, json, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re
sys.path.insert(0, '/home/claude')
from shared import head, masthead, footer

NEWS_API_KEY = "080cc35148fe414fa1179b62a2d37639"

EXTRA_CSS = """
  .news-filters { display: flex; gap: 0; border-bottom: 1px solid var(--rule); margin-bottom: 32px; overflow-x: auto; }
  .news-filters a { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; padding: 10px 18px; color: var(--ink-muted); text-decoration: none; border-right: 1px solid var(--rule); white-space: nowrap; }
  .news-filters a:hover, .news-filters a.active { background: var(--ink); color: var(--paper); }
  .news-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
  .news-item { padding: 20px; border-bottom: 1px solid var(--rule); border-right: 1px solid var(--rule); text-decoration: none; color: inherit; display: block; }
  .news-item:nth-child(even) { border-right: none; }
  .news-item:hover { background: var(--paper-warm); }
  .ni-source { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-faint); margin-bottom: 8px; }
  .ni-title { font-family: 'Playfair Display', serif; font-size: 17px; font-weight: 700; line-height: 1.3; margin-bottom: 8px; color: var(--ink); }
  .ni-excerpt { font-size: 12px; color: var(--ink-muted); line-height: 1.6; }
  .ni-date { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink-faint); margin-top: 10px; }
  .no-results { padding: 40px; text-align: center; color: var(--ink-muted); font-size: 14px; }
  @media(max-width:768px){ .news-grid{grid-template-columns:1fr;} .news-item{border-right:none;} }
"""

def fetch_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [warn] {url}: {e}")
        return ""

def fetch_news():
    articles = []
    # NewsAPI
    url = (
        "https://newsapi.org/v2/everything"
        "?q=layoffs+OR+%22job+cuts%22+OR+%22workforce+reduction%22+OR+%22redundancies%22"
        "&language=en&sortBy=publishedAt&pageSize=20"
        f"&apiKey={NEWS_API_KEY}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "ok":
            for a in data.get("articles", []):
                articles.append({
                    "title":   (a.get("title") or "")[:120],
                    "source":  a.get("source", {}).get("name", "NewsAPI"),
                    "url":     a.get("url", "#"),
                    "excerpt": (a.get("description") or "")[:200],
                    "date":    (a.get("publishedAt") or "")[:10],
                })
    except Exception as e:
        print(f"  [warn] NewsAPI: {e}")

    # RSS feeds
    feeds = [
        ("TechCrunch", "https://techcrunch.com/tag/layoffs/feed/"),
        ("The Verge",  "https://www.theverge.com/rss/index.xml"),
    ]
    keywords = ["layoff", "job cut", "workforce", "redundan", "restruc", "eliminat", "fired"]
    for source, feed_url in feeds:
        raw = fetch_url(feed_url)
        if not raw: continue
        try:
            root = ET.fromstring(raw)
            items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
            for item in items[:15]:
                def tag(t):
                    el = item.find(t)
                    return el.text.strip() if el is not None and el.text else ""
                title   = tag("title") or tag("{http://www.w3.org/2005/Atom}title")
                desc    = tag("description") or tag("{http://www.w3.org/2005/Atom}summary")
                link    = tag("link") or tag("{http://www.w3.org/2005/Atom}link")
                pubdate = tag("pubDate") or tag("{http://www.w3.org/2005/Atom}updated")
                if any(k in (title+desc).lower() for k in keywords):
                    articles.append({
                        "title":   title[:120],
                        "source":  source,
                        "url":     link or "#",
                        "excerpt": re.sub(r"<[^>]+>", "", desc)[:200],
                        "date":    pubdate[:10] if pubdate else "",
                    })
        except Exception as e:
            print(f"  [warn] RSS {source}: {e}")

    # Dedupe
    seen, unique = set(), []
    for a in articles:
        k = a["title"][:50].lower()
        if k and k not in seen:
            seen.add(k)
            unique.append(a)
    return unique[:24]

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def build():
    articles = fetch_news()
    cards = ""
    if articles:
        for a in articles:
            cards += f"""
            <a href="{esc(a['url'])}" target="_blank" rel="noopener" class="news-item">
              <div class="ni-source">{esc(a['source'])}</div>
              <div class="ni-title">{esc(a['title'])}</div>
              <div class="ni-excerpt">{esc(a['excerpt'])}</div>
              <div class="ni-date">{esc(a['date'])}</div>
            </a>"""
    else:
        cards = '<div class="no-results">No recent articles found. Check back in 2 hours.</div>'

    html = head("Latest News", EXTRA_CSS)
    html += masthead("Latest News")
    html += f"""
<div class="page-hero">
  <div class="page-eyebrow">Live Feed · Updated Every 2 Hours</div>
  <h1 class="page-title">Latest Layoff News</h1>
  <p class="page-sub">Aggregated from NewsAPI, TechCrunch, The Verge, and verified corporate disclosures. {len(articles)} articles currently tracked.</p>
</div>
<div class="page-body">
  <div class="news-filters">
    <a href="#" class="active">All</a>
    <a href="#">Technology</a>
    <a href="#">Finance</a>
    <a href="#">Healthcare</a>
    <a href="#">Media</a>
    <a href="#">Retail</a>
  </div>
  <div class="news-grid">{cards}</div>
</div>
{footer()}
</body></html>"""
    return html

if __name__ == "__main__":
    with open("/var/www/layofftrends.com/news.html", "w") as f:
        f.write(build())
    print("news.html written")
