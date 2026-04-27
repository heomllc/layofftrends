#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/claude')
from shared import head, masthead, footer, SHARED_CSS

EXTRA_CSS = """
  .sector-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 24px; margin-bottom: 48px; }
  .sector-card { border: 1px solid var(--rule); padding: 24px; background: var(--paper); }
  .sector-card:hover { background: var(--paper-warm); }
  .sc-name { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; margin-bottom: 6px; }
  .sc-count { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: var(--accent-red); margin-bottom: 4px; }
  .sc-pct { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-faint); margin-bottom: 14px; }
  .sc-bar-track { height: 6px; background: var(--paper-warm); border-radius: 1px; margin-bottom: 14px; }
  .sc-bar-fill { height: 6px; background: var(--ink); border-radius: 1px; }
  .sc-companies { font-size: 12px; color: var(--ink-muted); }
  .sc-companies strong { color: var(--ink); }
  .trend-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .trend-table th { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-faint); padding: 10px 12px; border-bottom: 2px solid var(--ink); text-align: left; }
  .trend-table td { padding: 12px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; }
  .trend-table tr:hover td { background: var(--paper-warm); }
  .trend-table .num { font-family: 'DM Mono', monospace; font-size: 13px; }
  .trend-table .neg { color: var(--accent-red); }
  .trend-table .pos { color: var(--accent-green); }
  @media(max-width:768px){ .sector-grid{grid-template-columns:1fr;} }
"""

SECTORS = [
    ("Technology",     82400, 100, 37, ["Intel", "Tesla", "Cisco", "Dell", "Spotify"], "+34%"),
    ("Finance",        34100,  41, 18, ["Citigroup", "Goldman Sachs", "Wells Fargo"], "+18%"),
    ("Healthcare",     22600,  27, 14, ["Pfizer", "Johnson & Johnson", "Merck"],       "+22%"),
    ("Retail & e-Com", 19800,  24, 12, ["Amazon", "Target", "Wayfair"],                "+11%"),
    ("Media",          14500,  17,  9, ["Warner Bros", "Paramount", "BuzzFeed"],       "+41%"),
    ("Manufacturing",  12100,  15,  8, ["Ford", "3M", "Honeywell"],                    "+8%"),
    ("Education",       8200,  10,  6, ["Chegg", "2U", "Coursera"],                    "+29%"),
    ("Real Estate",     5700,   7,  4, ["Zillow", "Opendoor", "Compass"],              "+15%"),
]

TREND_ROWS = [
    ("Q1 2026", "Technology",     "Intel",       "15,000", "Cost restructuring + AI pivot",        "neg"),
    ("Q1 2026", "Finance",        "Citigroup",    "4,200",  "AI-driven back-office automation",     "neg"),
    ("Q1 2026", "Media",          "Spotify",      "1,600",  "Generative AI content curation",       "neg"),
    ("Q1 2026", "Technology",     "Cisco",        "4,000",  "Network hardware demand decline",       "neg"),
    ("Q1 2026", "Technology",     "Tesla",       "14,000",  "EV demand softening, DOGE pressure",   "neg"),
    ("Q1 2026", "Healthcare",     "Pfizer",       "3,100",  "Post-COVID portfolio rightsizing",     "neg"),
    ("Q1 2026", "Retail",         "Amazon",       "2,800",  "Alexa + devices division cut",         "neg"),
    ("Q1 2026", "Technology",     "OpenAI",      "+1,500",  "Aggressive scaling across all orgs",   "pos"),
    ("Q1 2026", "Technology",     "Nvidia",      "+8,200",  "AI chip demand, massive expansion",    "pos"),
]

def build():
    cards = ""
    for name, count, bar, companies, examples, yoy in SECTORS:
        cards += f"""
        <div class="sector-card">
          <div class="sc-name">{name}</div>
          <div class="sc-count">{count:,}</div>
          <div class="sc-pct">{yoy} vs 2025 · {companies} companies reporting</div>
          <div class="sc-bar-track"><div class="sc-bar-fill" style="width:{bar}%"></div></div>
          <div class="sc-companies">Notable: <strong>{", ".join(examples)}</strong></div>
        </div>"""

    rows = ""
    for q, sector, company, count, reason, cls in TREND_ROWS:
        prefix = "" if cls == "pos" else ""
        rows += f"""
        <tr>
          <td>{q}</td>
          <td><span class="tag tag-{'blue' if cls=='pos' else 'red'}">{sector}</span></td>
          <td><strong>{company}</strong></td>
          <td class="num {cls}">{count}</td>
          <td style="color:var(--ink-muted);font-size:12px;">{reason}</td>
        </tr>"""

    html = head("Sector Analysis", EXTRA_CSS)
    html += masthead("Sector Analysis")
    html += f"""
<div class="page-hero">
  <div class="page-eyebrow">2026 Data · Updated Every 2 Hours</div>
  <h1 class="page-title">Displacement by Sector</h1>
  <p class="page-sub">A breakdown of workforce reductions across industries in 2026. Technology leads all sectors for the fourth consecutive year, driven by AI-driven automation and cost restructuring.</p>
</div>
<div class="page-body">
  <div class="section-head"><div class="section-title">Sector Overview</div></div>
  <div class="sector-grid">{cards}</div>

  <div class="section-head"><div class="section-title">Notable Restructuring Events — Q1 2026</div></div>
  <table class="trend-table">
    <thead>
      <tr>
        <th>Period</th><th>Sector</th><th>Company</th><th>Jobs</th><th>Driver</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>
{footer()}
</body></html>"""
    return html

if __name__ == "__main__":
    with open("/var/www/layofftrends.com/sectors.html", "w") as f:
        f.write(build())
    print("sectors.html written")
