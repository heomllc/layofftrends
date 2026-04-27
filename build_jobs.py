#!/usr/bin/env python3
import sys, json, urllib.request
sys.path.insert(0, '/home/claude')
from shared import head, masthead, footer

EXTRA_CSS = """
  .jobs-layout { display: grid; grid-template-columns: 1fr 300px; gap: 0; }
  .jobs-main { border-right: 1px solid var(--rule); padding-right: 36px; }
  .jobs-aside { padding-left: 28px; }
  .job-card { display: grid; grid-template-columns: 1fr auto; gap: 12px; align-items: start; padding: 18px 0; border-bottom: 1px solid var(--rule); text-decoration: none; color: inherit; }
  .job-card:hover .jc-title { color: var(--accent-blue); }
  .jc-title { font-family: 'Playfair Display', serif; font-size: 16px; font-weight: 700; margin-bottom: 4px; color: var(--ink); }
  .jc-company { font-size: 13px; font-weight: 600; color: var(--ink-muted); margin-bottom: 6px; }
  .jc-meta { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink-faint); letter-spacing: 0.06em; }
  .jc-apply { background: var(--ink); color: var(--paper); padding: 8px 16px; font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; border-radius: 2px; white-space: nowrap; align-self: center; }
  .jc-apply:hover { background: var(--accent-blue); }
  .jc-apply.linkedin { background: #0077b5; }
  .resource-card { border: 1px solid var(--rule); padding: 16px 18px; margin-bottom: 12px; }
  .resource-card:hover { background: var(--paper-warm); }
  .rc-title { font-weight: 600; font-size: 13px; margin-bottom: 4px; color: var(--ink); }
  .rc-desc { font-size: 12px; color: var(--ink-muted); line-height: 1.55; margin-bottom: 8px; }
  .rc-link { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--accent-blue); text-decoration: none; letter-spacing: 0.06em; }
  .tab-bar { display: flex; border-bottom: 2px solid var(--ink); margin-bottom: 24px; }
  .tab { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; padding: 10px 18px; cursor: pointer; color: var(--ink-muted); border-bottom: 3px solid transparent; margin-bottom: -2px; }
  .tab.active { color: var(--ink); border-bottom-color: var(--accent-red); }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }
  .li-search-box { display: flex; gap: 0; margin-bottom: 28px; border: 1px solid var(--rule); }
  .li-input { flex: 1; padding: 12px 16px; border: none; background: var(--paper); font-family: 'DM Sans', sans-serif; font-size: 14px; outline: none; color: var(--ink); }
  .li-btn { background: #0077b5; color: white; border: none; padding: 12px 20px; font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer; white-space: nowrap; }
  .li-btn:hover { background: #005e8b; }
  @media(max-width:768px){ .jobs-layout{grid-template-columns:1fr;} .jobs-main{border-right:none;padding-right:0;} .jobs-aside{padding-left:0;border-top:1px solid var(--rule);padding-top:24px;margin-top:32px;} }
"""

def fetch_remotive_jobs():
    url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=15"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        jobs = []
        for j in data.get("jobs", [])[:15]:
            jobs.append({
                "title":    j.get("title", ""),
                "company":  j.get("company_name", ""),
                "location": j.get("candidate_required_location", "Remote"),
                "type":     j.get("job_type", "full_time"),
                "url":      j.get("url", "#"),
                "source":   "remotive",
                "salary":   j.get("salary", ""),
            })
        return jobs
    except Exception as e:
        print(f"  [warn] Remotive: {e}")
        return []

RESOURCES = [
    ("Severance Negotiation Guide",     "How to evaluate and negotiate your severance package. Know your rights.", "https://www.dol.gov/agencies/whd"),
    ("Unemployment Benefits (DOL)",     "Apply for unemployment insurance. Federal resource for all US states.",  "https://www.careeronestop.org/LocalHelp/UnemploymentBenefits/find-unemployment-benefits.aspx"),
    ("LinkedIn Job Search",             "Search millions of open roles. Set job alerts for your target titles.",   "https://www.linkedin.com/jobs/"),
    ("Remotive — Remote Jobs",          "Curated remote tech jobs updated daily. Free to browse.",                 "https://remotive.com"),
    ("Adzuna — Tech Jobs",              "Aggregates jobs from hundreds of boards. Good salary data.",              "https://www.adzuna.com"),
    ("Layoffs.fyi Job Board",           "Job board specifically for laid-off tech workers. Community-driven.",     "https://layoffs.fyi"),
    ("COBRA Health Insurance Guide",    "Keep your employer health coverage after a layoff. Deadlines matter.",    "https://www.dol.gov/agencies/ebsa/laws-and-regulations/laws/cobra"),
    ("Coursera — Free Certificates",   "Audit thousands of courses free. Google, Meta, IBM certificates.",        "https://www.coursera.org"),
    ("AWS Free Training",               "Cloud certifications. AWS Skill Builder has 500+ free courses.",         "https://skillbuilder.aws"),
    ("Levels.fyi — Salary Data",        "Know your market rate before your next negotiation.",                    "https://www.levels.fyi"),
]

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def build():
    jobs = fetch_remotive_jobs()

    job_cards = ""
    for j in jobs:
        salary_str = f" · {esc(j['salary'])}" if j.get("salary") else ""
        job_cards += f"""
        <a href="{esc(j['url'])}" target="_blank" rel="noopener" class="job-card">
          <div>
            <div class="jc-title">{esc(j['title'])}</div>
            <div class="jc-company">{esc(j['company'])}</div>
            <div class="jc-meta">{esc(j['location'])} · {esc(j['type'].replace('_',' ').title())}{salary_str} · via Remotive</div>
          </div>
          <span class="jc-apply">Apply →</span>
        </a>"""

    if not job_cards:
        job_cards = "<p style='color:var(--ink-muted);padding:20px 0;font-size:13px;'>Live job listings temporarily unavailable. Check back shortly or use the LinkedIn search above.</p>"

    resource_cards = ""
    for title, desc, url in RESOURCES:
        resource_cards += f"""
        <a href="{url}" target="_blank" rel="noopener" class="resource-card" style="display:block;text-decoration:none;">
          <div class="rc-title">{title}</div>
          <div class="rc-desc">{desc}</div>
          <span class="rc-link">Visit →</span>
        </a>"""

    html = head("Jobs & Learning", EXTRA_CSS)
    html += masthead("Jobs & Learning")
    html += f"""
<div class="page-hero">
  <div class="page-eyebrow">Jobs · Upskilling · Benefits</div>
  <h1 class="page-title">Jobs & Learning</h1>
  <p class="page-sub">Live remote job listings from Remotive, direct LinkedIn search, and curated resources for severance, benefits, upskilling, and your next role.</p>
</div>
<div class="page-body">
  <div class="jobs-layout">
    <div class="jobs-main">
      <div class="tab-bar">
        <div class="tab active" onclick="switchTab('remote')">Remote Jobs (Live)</div>
        <div class="tab" onclick="switchTab('linkedin')">Search LinkedIn</div>
        <div class="tab" onclick="switchTab('resources')">Resources & Benefits</div>
      </div>

      <div class="tab-panel active" id="tab-remote">
        <p style="font-size:12px;color:var(--ink-muted);margin-bottom:20px;">{len(jobs)} live remote roles via Remotive · Updated every 2 hours</p>
        {job_cards}
      </div>

      <div class="tab-panel" id="tab-linkedin">
        <p style="font-size:13px;color:var(--ink-muted);margin-bottom:20px;">Search LinkedIn Jobs directly. Pre-filled with common post-layoff search terms — edit as needed.</p>
        <div class="li-search-box">
          <input class="li-input" id="liQuery" type="text" value="software engineer" placeholder="Job title, skill, or keyword" />
          <button class="li-btn" onclick="searchLinkedIn()">Search LinkedIn →</button>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:28px;">
          <button onclick="setLiQuery('software engineer remote')" style="font-family:'DM Mono',monospace;font-size:10px;padding:6px 12px;border:1px solid var(--rule);background:var(--paper);cursor:pointer;border-radius:2px;">Software Engineer</button>
          <button onclick="setLiQuery('product manager remote')" style="font-family:'DM Mono',monospace;font-size:10px;padding:6px 12px;border:1px solid var(--rule);background:var(--paper);cursor:pointer;border-radius:2px;">Product Manager</button>
          <button onclick="setLiQuery('data scientist remote')" style="font-family:'DM Mono',monospace;font-size:10px;padding:6px 12px;border:1px solid var(--rule);background:var(--paper);cursor:pointer;border-radius:2px;">Data Scientist</button>
          <button onclick="setLiQuery('UX designer remote')" style="font-family:'DM Mono',monospace;font-size:10px;padding:6px 12px;border:1px solid var(--rule);background:var(--paper);cursor:pointer;border-radius:2px;">UX Designer</button>
          <button onclick="setLiQuery('finance analyst remote')" style="font-family:'DM Mono',monospace;font-size:10px;padding:6px 12px;border:1px solid var(--rule);background:var(--paper);cursor:pointer;border-radius:2px;">Finance Analyst</button>
          <button onclick="setLiQuery('devops engineer remote')" style="font-family:'DM Mono',monospace;font-size:10px;padding:6px 12px;border:1px solid var(--rule);background:var(--paper);cursor:pointer;border-radius:2px;">DevOps Engineer</button>
        </div>
        <a href="https://www.linkedin.com/jobs/search/?keywords=software+engineer&f_WT=2" target="_blank" rel="noopener" style="display:block;background:#0077b5;color:white;text-align:center;padding:14px;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border-radius:2px;" id="liLink">Open LinkedIn Jobs →</a>
      </div>

      <div class="tab-panel" id="tab-resources">
        {resource_cards}
      </div>
    </div>

    <aside class="jobs-aside">
      <div class="section-head"><div class="section-title">Quick Links</div></div>
      <ul style="list-style:none;">
        <li style="padding:10px 0;border-bottom:1px dashed var(--rule);font-size:13px;"><a href="https://www.linkedin.com/jobs/" target="_blank" style="color:var(--ink);text-decoration:none;">→ LinkedIn Jobs</a></li>
        <li style="padding:10px 0;border-bottom:1px dashed var(--rule);font-size:13px;"><a href="https://remotive.com" target="_blank" style="color:var(--ink);text-decoration:none;">→ Remotive Remote Jobs</a></li>
        <li style="padding:10px 0;border-bottom:1px dashed var(--rule);font-size:13px;"><a href="https://www.adzuna.com" target="_blank" style="color:var(--ink);text-decoration:none;">→ Adzuna Job Search</a></li>
        <li style="padding:10px 0;border-bottom:1px dashed var(--rule);font-size:13px;"><a href="https://layoffs.fyi" target="_blank" style="color:var(--ink);text-decoration:none;">→ Layoffs.fyi Board</a></li>
        <li style="padding:10px 0;border-bottom:1px dashed var(--rule);font-size:13px;"><a href="https://www.levels.fyi" target="_blank" style="color:var(--ink);text-decoration:none;">→ Salary Data (Levels.fyi)</a></li>
        <li style="padding:10px 0;font-size:13px;"><a href="https://skillbuilder.aws" target="_blank" style="color:var(--ink);text-decoration:none;">→ AWS Free Training</a></li>
      </ul>

      <div style="margin-top:32px;padding-top:24px;border-top:1px solid var(--rule);">
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-faint);margin-bottom:12px;">Know of a layoff?</div>
        <p style="font-size:12px;color:var(--ink-muted);line-height:1.65;margin-bottom:12px;">Submit an anonymous tip to the Whisper Network.</p>
        <a href="/whisper.html" style="display:block;background:var(--ink);color:var(--paper);text-align:center;padding:10px;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border-radius:2px;">Submit a Tip →</a>
      </div>
    </aside>
  </div>
</div>
{footer()}
<script>
function switchTab(id) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  event.target.classList.add('active');
}}
function setLiQuery(q) {{
  document.getElementById('liQuery').value = q;
  const encoded = encodeURIComponent(q);
  document.getElementById('liLink').href = `https://www.linkedin.com/jobs/search/?keywords=${{encoded}}&f_WT=2`;
}}
function searchLinkedIn() {{
  const q = document.getElementById('liQuery').value.trim();
  if (!q) return;
  window.open('https://www.linkedin.com/jobs/search/?keywords=' + encodeURIComponent(q) + '&f_WT=2', '_blank');
}}
</script>
</body></html>"""
    return html

if __name__ == "__main__":
    with open("/var/www/layofftrends.com/jobs.html", "w") as f:
        f.write(build())
    print("jobs.html written")
