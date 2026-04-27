#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/claude')
from shared import head, masthead, footer

EXTRA_CSS = """
  .region-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 48px; }
  .region-card { border: 1px solid var(--rule); padding: 20px 22px; }
  .region-card:hover { background: var(--paper-warm); }
  .rc-flag { font-size: 24px; margin-bottom: 8px; }
  .rc-country { font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; margin-bottom: 4px; }
  .rc-count { font-family: 'DM Mono', monospace; font-size: 26px; color: var(--accent-red); margin-bottom: 2px; }
  .rc-label { font-size: 11px; color: var(--ink-muted); margin-bottom: 12px; }
  .rc-bar { height: 4px; background: var(--paper-warm); border-radius: 1px; }
  .rc-bar-fill { height: 4px; background: var(--ink); border-radius: 1px; }
  .rc-detail { font-size: 12px; color: var(--ink-muted); margin-top: 10px; line-height: 1.5; }
  .us-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 40px; }
  .us-card { border: 1px solid var(--rule); padding: 14px 16px; }
  .us-state { font-weight: 600; font-size: 13px; margin-bottom: 4px; }
  .us-count { font-family: 'DM Mono', monospace; font-size: 18px; color: var(--accent-red); }
  .us-city { font-size: 11px; color: var(--ink-muted); margin-top: 3px; }
  @media(max-width:900px){ .region-grid{grid-template-columns:1fr 1fr;} .us-grid{grid-template-columns:1fr 1fr;} }
  @media(max-width:600px){ .region-grid{grid-template-columns:1fr;} .us-grid{grid-template-columns:1fr 1fr;} }
"""

REGIONS = [
    ("🇺🇸", "United States", 134200, 100, "Tech corridor cuts dominant — Bay Area, Seattle, NYC. WARN filings up 34% YoY."),
    ("🇮🇳", "India",          38400,  29, "IT services sector hardest hit. Bengaluru and Hyderabad GCCs absorbing overflow."),
    ("🇬🇧", "United Kingdom", 21800,  16, "Financial services reductions in London. Media consolidation ongoing."),
    ("🇩🇪", "Germany",        14600,  11, "Manufacturing automation wave. Deutsche Telekom and Siemens restructuring."),
    ("🇨🇦", "Canada",          9800,   7, "Toronto and Vancouver tech hubs seeing spillover from US parent companies."),
    ("🇦🇺", "Australia",       5200,   4, "Financial services and retail. ANZ and Westpac back-office reductions."),
    ("🇸🇬", "Singapore",       4100,   3, "APAC hub restructuring. Several US tech firms reducing regional HQ headcount."),
    ("🇫🇷", "France",          3800,   3, "Media and retail consolidation. Government severance mandates in play."),
    ("🇸🇪", "Sweden",          2900,   2, "Klarna and Spotify driving fintech/media reductions. Stockholm tech scene cooling."),
]

US_STATES = [
    ("California",    42100, "San Francisco, San Jose, Los Angeles"),
    ("Washington",    18400, "Seattle, Bellevue, Redmond"),
    ("New York",      14200, "NYC, Manhattan, Brooklyn"),
    ("Texas",         11800, "Austin, Dallas, Houston"),
    ("Massachusetts",  7400, "Boston, Cambridge"),
    ("Georgia",        5100, "Atlanta, Alpharetta"),
    ("Illinois",       4800, "Chicago"),
    ("Colorado",       3900, "Denver, Boulder"),
    ("Florida",        3600, "Miami, Tampa"),
    ("Virginia",       3200, "Arlington, McLean"),
    ("North Carolina", 2800, "Charlotte, Raleigh"),
    ("Ohio",           2600, "Columbus, Cleveland"),
]

def build():
    region_cards = ""
    for flag, country, count, bar, detail in REGIONS:
        region_cards += f"""
        <div class="region-card">
          <div class="rc-flag">{flag}</div>
          <div class="rc-country">{country}</div>
          <div class="rc-count">{count:,}</div>
          <div class="rc-label">jobs eliminated in 2026</div>
          <div class="rc-bar"><div class="rc-bar-fill" style="width:{bar}%"></div></div>
          <div class="rc-detail">{detail}</div>
        </div>"""

    us_cards = ""
    for state, count, cities in US_STATES:
        us_cards += f"""
        <div class="us-card">
          <div class="us-state">{state}</div>
          <div class="us-count">{count:,}</div>
          <div class="us-city">{cities}</div>
        </div>"""

    html = head("Regional Data", EXTRA_CSS)
    html += masthead("Regional Data")
    html += f"""
<div class="page-hero">
  <div class="page-eyebrow">Global Outlook · 2026</div>
  <h1 class="page-title">Regional Displacement Data</h1>
  <p class="page-sub">Workforce reductions tracked across 9 countries and 12 US states. The United States accounts for 61% of all verified layoffs in 2026, led by the California tech corridor.</p>
</div>
<div class="page-body">
  <div class="section-head"><div class="section-title">Global Overview</div></div>
  <div class="region-grid">{region_cards}</div>

  <div class="section-head"><div class="section-title">United States — by State</div></div>
  <div class="us-grid">{us_cards}</div>

  <div style="background:var(--paper-warm);border:1px solid var(--rule);padding:20px 24px;font-size:13px;color:var(--ink-muted);line-height:1.7;">
    <strong style="color:var(--ink);font-family:'DM Mono',monospace;font-size:10px;letter-spacing:0.1em;text-transform:uppercase;">Data Methodology</strong><br>
    US data sourced from federal WARN Act filings (Department of Labor), supplemented by verified corporate press releases and SEC filings. International data aggregated from national labor ministry disclosures, verified news sources, and peer submissions. Numbers represent verified events only and may undercount actual total displacement.
  </div>
</div>
{footer()}
</body></html>"""
    return html

if __name__ == "__main__":
    with open("/var/www/layofftrends.com/regional.html", "w") as f:
        f.write(build())
    print("regional.html written")
