#!/usr/bin/env python3
"""One-off: correct `modified` in page_dates.json to the date of the last commit that changed a
page's content in more than its date stamps (the old builders re-stamped every page on every run,
so git's own last-commit date and the sitemap <lastmod> both overstate changes).
Run from the repo root after a baseline build:  python3 build-cities/seed_page_dates.py"""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(ROOT, "build-cities", "page_dates.json")
SITE = "https://www.snowdayforecaster.com"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
def git(*a): return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout
db = json.load(open(STORE))
for url, rec in db.items():
    path = url[len(SITE) + 1:] + "index.html"
    revs = [l.split() for l in git("log", "--format=%H %cs", "--", path).splitlines()]  # newest first
    if not revs: continue
    real = revs[-1][1]
    for (h_new, d_new), (h_old, _) in zip(revs, revs[1:] + [(None, None)]):
        if h_old is None: real = d_new; break
        a = DATE.sub("D", git("show", f"{h_new}:{path}")); b = DATE.sub("D", git("show", f"{h_old}:{path}"))
        if a != b: real = d_new; break
    rec["modified"] = real
json.dump(dict(sorted(db.items())), open(STORE, "w"), indent=1); open(STORE, "a").write("\n")
import collections; print(collections.Counter(r["modified"] for r in db.values()))
