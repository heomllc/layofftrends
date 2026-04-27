#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/claude')
from shared import head, masthead, footer

EXTRA_CSS = """
  .about-layout { display: grid; grid-template-columns: 1fr 320px; gap: 0; }
  .about-main { border-right: 1px solid var(--rule); padding-right: 40px; }
  .about-aside { padding-left: 32px; }
  .prose h2 { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; margin: 32px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--rule); }
  .prose p { font-size: 14px; color: var(--ink-muted); line-height: 1.8; margin-bottom: 16px; }
  .prose ul { list-style: none; margin-bottom: 16px; }
  .prose ul li { font-size: 14px; color: var(--ink-muted); padding: 6px 0; border-bottom: 1px dashed var(--rule); padding-left: 16px; position: relative; }
  .prose ul li::before { content: '→'; position: absolute; left: 0; color: var(--accent-red); font-family: 'DM Mono', monospace; font-size: 11px; }
  .stat-row { display: grid; grid-template-columns: repeat(2,1fr); gap: 12px; margin-bottom: 32px; }
  .stat-box { border: 1px solid var(--rule); padding: 18px 20px; }
  .stat-val { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: var(--accent-red); margin-bottom: 4px; }
  .stat-lbl { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-faint); }
  .source-card { border: 1px solid var(--rule); padding: 14px 16px; margin-bottom: 10px; }
  .source-name { font-weight: 600; font-size: 13px; margin-bottom: 3px; }
  .source-desc { font-size: 12px; color: var(--ink-muted); line-height: 1.55; }
  .source-type { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-faint); margin-top: 4px; }
  @media(max-width:768px){ .about-layout{grid-template-columns:1fr;} .about-main{border-right:none;padding-right:0;} .about-aside{padding-left:0;border-top:1px solid var(--rule);padding-top:24px;margin-top:32px;} }
"""

SOURCES = [
    ("WARN Act (DOL)", "US Department of Labor federal filings. Companies with 100+ employees must file 60 days before mass layoffs.", "Government · Official"),
    ("NewsAPI", "Aggregated news from 70,000+ sources worldwide. Filtered for layoff-related content.", "News Aggregator · API"),
    ("TechCrunch RSS", "Real-time feed from TechCrunch's layoff coverage. Filtered by keyword.", "RSS Feed · Free"),
    ("The Verge RSS", "Technology and media news. Filtered for workforce reduction stories.", "RSS Feed · Free"),
    ("Remotive API", "Remote job listings API. Powers the Jobs & Learning page with live openings.", "Jobs API · Free"),
    ("Whisper Network", "Anonymous peer submissions from workers inside affected companies. Verified where possible.", "Community · Anonymous"),
    ("Layoffs.fyi", "Community-maintained tracker. Used as secondary validation source.", "Community · Reference"),
]

def build():
    source_cards = ""
    for name, desc, stype in SOURCES:
        source_cards += f"""
        <div class="source-card">
          <div class="source-name">{name}</div>
          <div class="source-desc">{desc}</div>
          <div class="source-type">{stype}</div>
        </div>"""

    html = head("About", EXTRA_CSS)
    html += masthead("About")
    html += f"""
<div class="page-hero">
  <div class="page-eyebrow">Independent · Free · Open</div>
  <h1 class="page-title">About LayoffTrends</h1>
  <p class="page-sub">An independent real-time tracker for workforce displacement. No ads. No paywalls. No agenda. Just verified data published openly.</p>
</div>
<div class="page-body">
  <div class="about-layout">
    <div class="about-main">
      <div class="stat-row">
        <div class="stat-box"><div class="stat-val">218K+</div><div class="stat-lbl">Jobs tracked in 2026</div></div>
        <div class="stat-box"><div class="stat-val">1,247</div><div class="stat-lbl">Active WARN notices</div></div>
        <div class="stat-box"><div class="stat-val">47</div><div class="stat-lbl">Industries covered</div></div>
        <div class="stat-box"><div class="stat-val">2hrs</div><div class="stat-lbl">Data refresh interval</div></div>
      </div>

      <div class="prose">
        <h2>What We Do</h2>
        <p>LayoffTrends aggregates publicly available data from government WARN Act filings, corporate press releases, SEC disclosures, and verified news sources to produce a real-time picture of workforce displacement across industries and geographies.</p>
        <p>The site rebuilds automatically every two hours, pulling fresh data from our source network and republishing updated figures. No manual editorial process. No spin. Just the numbers as they come in.</p>

        <h2>Why We Built This</h2>
        <p>Layoff data is fragmented across hundreds of sources — government portals, company press releases, news articles, and social media. Workers deserve a single, clean, honest view of what's happening in the labor market. That's what this is.</p>
        <p>The Whisper Network exists because official channels lag reality by weeks. When someone inside a company knows what's coming, that signal is valuable to thousands of workers who can start preparing now.</p>

        <h2>Data Methodology</h2>
        <p>Numbers on this site represent verified events only. A "verified" layoff is one with at least one of: a WARN Act filing, a corporate press release, an SEC 8-K filing, or two independent news sources. Whisper Network submissions are labeled Unverified until corroborated.</p>
        <ul>
          <li>WARN Act filings are the gold standard — legally required, filed 60 days in advance</li>
          <li>Corporate announcements are taken at face value but checked against WARN where possible</li>
          <li>News articles are used as secondary validation only</li>
          <li>Peer tips are published as-is with an Unverified label until corroborated</li>
          <li>International data relies on national equivalents of WARN and news coverage</li>
        </ul>

        <h2>What We Are Not</h2>
        <p>We are not financial advisors. Nothing on this site constitutes investment advice. We are not affiliated with any company, recruiter, or government body. We do not sell data, run ads, or monetize user information in any way.</p>

        <h2>Contact</h2>
        <p>To submit a tip anonymously, use the <a href="/whisper.html" style="color:var(--ink);">Whisper Network</a>. For press inquiries or data corrections, the site is community-maintained — submit corrections via the whisper form with the tag [CORRECTION].</p>
      </div>
    </div>

    <aside class="about-aside">
      <div style="padding:16px;background:var(--paper-warm);border:1px solid var(--rule);font-size:12px;color:var(--ink-muted);line-height:1.7;margin-bottom:16px;">
        <strong style="color:var(--ink);display:block;margin-bottom:6px;">Update Schedule</strong>
        This site rebuilds every 2 hours via an automated Python script. Data freshness timestamp is shown in the site header.
      </div>
      <div style="padding:16px;background:var(--paper-warm);border:1px solid var(--rule);font-size:12px;color:var(--ink-muted);line-height:1.7;">
        <strong style="color:var(--ink);display:block;margin-bottom:6px;">Submit a Tip</strong>
        Know about an upcoming layoff? Share it anonymously on the Whisper Network.
        <a href="/whisper.html" style="display:block;margin-top:10px;background:var(--ink);color:var(--paper);text-align:center;padding:9px;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border-radius:2px;">Go to Whisper Network →</a>
      </div>
    </aside>
  </div>
</div>
{footer()}
</body></html>"""
    return html

if __name__ == "__main__":
    with open("/var/www/layofftrends.com/about.html", "w") as f:
        f.write(build())
    print("about.html written")
