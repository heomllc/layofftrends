SHARED_CSS = """
  :root {
    --ink: #0f0f0f;
    --ink-muted: #4a4a4a;
    --ink-faint: #9a9a9a;
    --paper: #f7f4ef;
    --paper-warm: #ede9e2;
    --rule: #d4cfc7;
    --accent-red: #c8352a;
    --accent-amber: #d4820a;
    --accent-green: #2a7d4f;
    --accent-blue: #1a4d8c;
    --col-width: 1200px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--paper); color: var(--ink); font-family: 'DM Sans', sans-serif; font-size: 15px; line-height: 1.6; }
  .masthead { border-bottom: 3px solid var(--ink); background: var(--paper); position: sticky; top: 0; z-index: 100; }
  .masthead-top { display: flex; align-items: center; justify-content: space-between; padding: 10px 32px; border-bottom: 1px solid var(--rule); font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-muted); letter-spacing: 0.04em; }
  .live-badge { display: flex; align-items: center; gap: 6px; color: var(--accent-red); font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; font-size: 10px; }
  .live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent-red); animation: pulse 1.4s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.85)} }
  .masthead-brand { padding: 14px 32px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .wordmark { font-family: 'Playfair Display', serif; font-weight: 900; font-size: 36px; letter-spacing: -0.03em; color: var(--ink); text-decoration: none; line-height: 1; flex-shrink: 0; }
  .wordmark span { color: var(--accent-red); }
  .brand-pillars { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .brand-pillar { font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 600; color: var(--ink-muted); text-decoration: none; padding: 7px 16px; border: 1px solid var(--rule); border-radius: 2px; letter-spacing: 0.01em; transition: all 0.15s; white-space: nowrap; }
  .brand-pillar:hover { background: var(--paper-warm); color: var(--ink); border-color: var(--ink-muted); }
  .brand-pillar.active { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  @media(max-width:900px){ .brand-pillars { display: none; } }
  .masthead-nav { display: flex; border-top: 1px solid var(--rule); padding: 0 24px; overflow-x: auto; }
  .masthead-nav a { font-family: 'DM Sans', sans-serif; font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-muted); text-decoration: none; padding: 10px 14px; border-right: 1px solid var(--rule); white-space: nowrap; transition: color .15s, background .15s; }
  .masthead-nav a:first-child { border-left: 1px solid var(--rule); }
  .masthead-nav a:hover, .masthead-nav a.active { color: var(--ink); background: var(--paper-warm); }
  .page-hero { max-width: var(--col-width); margin: 0 auto; padding: 40px 32px 32px; border-left: 1px solid var(--rule); border-right: 1px solid var(--rule); border-bottom: 2px solid var(--ink); }
  .page-eyebrow { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--accent-red); margin-bottom: 10px; }
  .page-title { font-family: 'Playfair Display', serif; font-size: 44px; font-weight: 900; line-height: 1.08; letter-spacing: -0.02em; margin-bottom: 12px; }
  .page-sub { font-size: 15px; color: var(--ink-muted); max-width: 600px; line-height: 1.65; }
  .page-body { max-width: var(--col-width); margin: 0 auto; padding: 36px 32px 60px; border-left: 1px solid var(--rule); border-right: 1px solid var(--rule); }
  .section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid var(--ink); margin-top: 40px; }
  .section-head:first-child { margin-top: 0; }
  .section-title { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; }
  footer { background: var(--ink); color: #aaa; padding: 32px; font-family: 'DM Mono', monospace; font-size: 11px; margin-top: 60px; }
  .footer-inner { max-width: var(--col-width); margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
  .footer-brand { font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 900; color: #f0ece4; }
  .footer-brand span { color: var(--accent-red); }
  .footer-links { display: flex; gap: 24px; list-style: none; }
  .footer-links a { color: #888; text-decoration: none; }
  .footer-links a:hover { color: #f0ece4; }
  .tag { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase; padding: 2px 8px; border-radius: 2px; font-weight: 500; }
  .tag-red { background:#fde8e8;color:var(--accent-red) }
  .tag-amber { background:#fef3dc;color:var(--accent-amber) }
  .tag-green { background:#e2f5ec;color:var(--accent-green) }
  .tag-blue { background:#e0ecff;color:var(--accent-blue) }
  @media(max-width:768px){
    .masthead-brand{padding:12px 16px;}
    .page-hero,.page-body{padding-left:16px;padding-right:16px;}
    .page-title{font-size:32px;}
    .footer-inner{flex-direction:column;gap:16px;}
  }
"""

def nav(active=""):
    pages = [
        ("/", "Live Dashboard"),
        ("/sectors.html", "Sector Analysis"),
        ("/regional.html", "Regional Data"),
        ("/news.html", "Latest News"),
        ("/whisper.html", "Whisper Network"),
        ("/jobs.html", "Jobs & Learning"),
        ("/about.html", "About"),
    ]
    links = ""
    for href, label in pages:
        cls = ' class="active"' if label == active else ""
        links += f'<a href="{href}"{cls}>{label}</a>'
    return links

def masthead(active=""):
    # Map page labels to which pillar is active
    pillar_map = {
        "Live Dashboard":     "market",
        "Sector Analysis":    "market",
        "Regional Data":      "market",
        "Latest News":        "market",
        "Jobs & Learning":    "jobs",
        "Whisper Network / Tips": "whisper",
        "About":              "",
    }
    current = pillar_map.get(active, "")
    p_market  = ' active' if current == "market"  else ""
    p_jobs    = ' active' if current == "jobs"    else ""
    p_whisper = ' active' if current == "whisper" else ""

    return f"""
<header class="masthead">
  <div class="masthead-top">
    <div class="live-badge"><div class="live-dot"></div>Live Data Feed</div>
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:var(--ink-faint);letter-spacing:0.04em;">Updated every 2 hours</div>
    <div style="font-size:10px;font-family:'DM Mono',monospace;color:var(--ink-faint);">layofftrends.com</div>
  </div>
  <div class="masthead-brand">
    <a href="/" class="wordmark">Layoff<span>Trends</span></a>
    <div class="brand-pillars">
      <a href="/" class="brand-pillar{p_market}">📊 Know the Market</a>
      <a href="/jobs.html" class="brand-pillar{p_jobs}">💼 Find Jobs</a>
      <a href="/whisper.html" class="brand-pillar{p_whisper}">🔊 Share Your Experience</a>
    </div>
  </div>
  <nav class="masthead-nav">{nav(active)}</nav>
</header>"""

def footer():
    return """
<footer>
  <div class="footer-inner">
    <div class="footer-brand">Layoff<span>Trends</span></div>
    <ul class="footer-links">
      <li><a href="/">Dashboard</a></li>
      <li><a href="/about.html">About</a></li>
      <li><a href="/whisper.html">Submit a Tip</a></li>
    </ul>
    <div style="color:#555;font-size:10px;">© 2026 LayoffTrends · Updated every 2 hours</div>
  </div>
</footer>"""

def head(title, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — LayoffTrends</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
{SHARED_CSS}
{extra_css}
</style>
</head>
<body>"""
