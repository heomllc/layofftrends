#!/usr/bin/env python3
"""
LayoffTrends — Master Build Script
Runs every 2 hours via cron. Rebuilds all pages.
"""
import subprocess, sys
from datetime import datetime, timezone

scripts = [
    ("/root/update_site.py",    "Homepage (index.html)"),
    ("/root/build_sectors.py",  "Sector Analysis"),
    ("/root/build_regional.py", "Regional Data"),
    ("/root/build_news.py",     "Latest News"),
   # ("/root/build_whisper.py",  "Whisper Network"),
    ("/root/build_jobs.py",     "Jobs & Learning"),
    ("/root/build_about.py",    "About"),
]

print(f"\n{'='*55}")
print(f"LayoffTrends full rebuild — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
print(f"{'='*55}")

errors = []
for script, label in scripts:
    print(f"\n▶ Building: {label}")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ Done")
        if result.stdout.strip():
            print(f"  {result.stdout.strip()}")
    else:
        print(f"  ❌ Error:")
        print(f"  {result.stderr.strip()[:300]}")
        errors.append(label)

print(f"\n{'='*55}")
if errors:
    print(f"⚠️  Completed with errors in: {', '.join(errors)}")
else:
    print(f"✅ All pages rebuilt successfully")
print(f"{'='*55}\n")
