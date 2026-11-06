"""Real publish / modified dates for generated pages.

Builders used to stamp every page with today's date on every run, so the sitemap told Google that
all pages changed whenever any builder ran. This module keeps one record per URL in
build-cities/page_dates.json:

    {url: {"hash": <sha256 of the page's content>, "published": "YYYY-MM-DD", "modified": "YYYY-MM-DD"}}

- `modified` moves to today only when the content hash changes.
- `published` is set once: the date git first saw the file, else today for a brand-new page.
- On the first run for a URL with no record, `modified` is seeded from the URL's current
  <lastmod> in sitemap.xml, so adopting this module does not by itself bump any date.

Pass the content that a reader would see (title, description, body). Do not include the dates
this module returns, or the hash would change every time they do.
"""
import datetime, hashlib, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "page_dates.json")
TODAY = datetime.date.today().isoformat()

_db = None
_sitemap = None

def _load():
    global _db, _sitemap
    if _db is None:
        _db = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {}
        sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
        _sitemap = dict(re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", sm))
    return _db

def _git_first_seen(path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cs", "--", path],
                             cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.split()
        return out[-1] if out else None
    except Exception:
        return None

HASH_VERSION = 2   # 2 = title + meta description + <main>; chrome (head tags, header, footer) is ignored

def content_of(page):
    """What a reader sees: title, meta description and the <main> block. Head/footer changes
    (a new meta tag, a footer link) are not content changes and must not move dateModified."""
    t = re.search(r"<title>(.*?)</title>", page, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', page)
    m = re.search(r"<main\b.*?</main>", page, re.S)
    if not m:
        return page
    return (t.group(1) if t else "") + "\n" + (d.group(1) if d else "") + "\n" + m.group(0)

def stamp(url, content, path=None):
    """Return (published, modified) for url, given the page's rendered content."""
    db = _load()
    h = hashlib.sha256(content_of(content).encode("utf-8")).hexdigest()
    rec = db.get(url)
    if rec is not None and rec.get("hv") != HASH_VERSION:
        rec.update(hash=h, hv=HASH_VERSION)      # re-baseline on a hashing change; dates untouched
    if rec is None:
        published = (path and _git_first_seen(os.path.relpath(path, ROOT))) or TODAY
        seeded = _sitemap.get(url)
        rec = {"hash": h, "hv": HASH_VERSION, "published": published, "modified": seeded or TODAY}
        db[url] = rec
    elif rec["hash"] != h:
        rec["hash"], rec["modified"] = h, TODAY
    return rec["published"], rec["modified"]

PUB = "__DATE_PUBLISHED__"   # builders put these in JSON-LD; write_page swaps in the real dates
MOD = "__DATE_MODIFIED__"

def write_page(path, url, page):
    """Hash the page with date placeholders still in it, then write it with real dates."""
    published, modified = stamp(url, page, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(page.replace(PUB, published).replace(MOD, modified))
    return published, modified

def latest():
    db = _load()
    return max((r["modified"] for r in db.values()), default=TODAY)

def lastmod(url, default=None):
    db = _load()
    return db.get(url, {}).get("modified") or _sitemap.get(url) or default or TODAY

def save():
    if _db is not None:
        json.dump(dict(sorted(_db.items())), open(STORE, "w", encoding="utf-8"), indent=1)
        open(STORE, "a").write("\n")
