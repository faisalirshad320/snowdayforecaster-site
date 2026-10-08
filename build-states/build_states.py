#!/usr/bin/env python3
"""Regenerate /states/<xx>/index.html, /states/index.html, /api/states.json and the state entries
in sitemap.xml from states_data.py. Page chrome (styles, header, footer, model script) is lifted
from the live homepage so the pages stay visually identical to the rest of the site.

Run from the repo root:  python3 build-states/build_states.py
"""
import json, os, re, sys, html, datetime
sys.path.insert(0, os.path.dirname(__file__))
from states_data import STATES, TIERS, TIER_TEXT, SEASON

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.snowdayforecaster.com"
TODAY = datetime.date.today().isoformat()
E = html.escape

# ---------- chrome from the live homepage ----------
home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
STYLE = home[home.find("<style>"):home.find("</style>") + 8]
HEADER = home[home.find("<header"):home.find("</header>") + 9]
FOOTER = home[home.find("<footer"):home.find("</footer>") + 9]
COEF = re.search(r"<script>window\.SDF_COEF=.*?</script>", home, re.S).group(0)
ORG = json.loads(home[home.find('<script type="application/ld+json">') + 35:home.find("</script>", home.find('<script type="application/ld+json">'))])[0]

EXTRA_CSS = """<style>
.sb{font-size:15px}.sb td,.sb th{padding:9px 8px}.sb-pct{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.sb-pct:before{content:"";width:9px;height:9px;border-radius:50%;background:var(--b0)}.sb-pct.b1:before{background:var(--b1)}.sb-pct.b2:before{background:var(--b2)}
.sb-pct.b3:before{background:var(--b3)}.sb-pct.b4:before{background:var(--b4)}.sb-pct.b5:before{background:var(--b5)}
.sb-why{color:var(--muted);font-size:14px}.sb-wk{color:var(--muted)}#stateboard[aria-busy=true]{min-height:120px;opacity:.6}
.sb-summary{font-size:15px;color:var(--muted);margin:8px 0 0;min-height:1.4em}
.zipcta{display:flex;gap:8px;margin:14px 0 0;flex-wrap:wrap}.zipcta input{flex:1;min-width:140px;font:inherit;font-size:18px;letter-spacing:.06em;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);min-height:48px}
.zipcta button{background:var(--accent);color:var(--accent-ink);border:0;border-radius:10px;padding:0 18px;font-weight:700;min-height:48px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 0}.chips a{font-size:14px;text-decoration:none;border:1px solid var(--line);border-radius:99px;padding:6px 12px;color:var(--ink);background:var(--card)}.chips a:hover{border-color:var(--accent)}
</style>"""

# ---------- zip shards for coordinates ----------
_shards = {}
def zip_info(z):
    sh = z[:2]
    if sh not in _shards:
        _shards[sh] = json.load(open(os.path.join(ROOT, "zip", sh + ".json")))
    e = _shards[sh][z]
    return dict(lat=e[0], lon=e[1], place=e[2], st=e[3])

# ---------- per-state bits preserved from the existing pages ----------
def existing_bits(code):
    p = os.path.join(ROOT, "states", code.lower(), "index.html")
    if not os.path.exists(p):
        return None, None
    s = open(p, encoding="utf-8").read()
    basis = re.search(r"<dt>Basis</dt><dd>(.*?)</dd>", s, re.S)
    table = re.search(r"<h2>What happened in .*?</h2>(.*?)(?=<h2>)", s, re.S)
    return (basis.group(1).strip() if basis else None), (table.group(1).strip() if table else None)

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"

def fmt_in(x):
    return ("%g" % x) + (" inch" if x == 1 else " inches")

# ---------- one state page ----------
def build_state(code, d):
    name, tier = d["name"], TIERS[d["tier"]]
    url = f"{SITE}/states/{code.lower()}/"
    basis, table = existing_bits(code)
    tracked = bool(table)
    if not basis:
        basis = f"{name} has no tracked district yet, so these are {tier['label']} regional figures."
    cities = []
    for cname, z, snow in d["cities"]:
        zi = zip_info(z)
        cities.append(dict(name=cname, zip=z, lat=zi["lat"], lon=zi["lon"], st=code, snow=snow))
    snowiest = max(cities, key=lambda c: c["snow"])
    least = min(cities, key=lambda c: c["snow"])
    big = cities[0]
    s50, s80, cold = tier["s50"], tier["s80"], tier["cold"]

    title = f"{name} Snow Day Calculator: Chance of a Snow Day Tomorrow by City"
    desc = (f"Will schools close tomorrow in {name}? Live snow day chances for {', '.join(c['name'].split(' (')[0] for c in cities[:4])} and more, "
            f"plus how much snow closes {name} schools ({s50} in for a 50% chance) and where closings are announced.")
    h1 = f"Snow day chances in {name} tomorrow"
    lede = f"A live snow day calculator for {name}: the chance school closes tomorrow in each major city, how much snow it takes, and where {name} districts announce closings."

    # --- live board ---
    board = (
        f'<h2 id="live">Will schools close tomorrow in {E(name)}?</h2>'
        f'<p>The board runs the <a href="/methodology/">published model</a> on the latest forecast for {len(cities)} {E(name)} '
        f'{"locations" if code == "DC" else "cities"}. It is a probability from the weather, not an announcement — '
        f'{E(name)} districts make their own call, usually the night before or by 5:30 a.m.</p>'
        f'<p class="sb-summary" id="sb-summary">Loading the latest forecast…</p>'
        f'<div id="stateboard" aria-live="polite"><p class="note">Loading tomorrow\'s chances…</p></div>'
        f'<form class="zipcta" action="/" method="get"><label for="zipcta" class="visually-hidden" style="position:absolute;left:-9999px">ZIP code</label>'
        f'<input id="zipcta" name="zip" inputmode="numeric" pattern="[0-9]{{5}}" maxlength="5" placeholder="Your {E(name)} ZIP code" required>'
        f'<button type="submit">Check my ZIP</button></form>'
        f'<p class="note">Chances are cached for 30 minutes in your browser. Forecast: Open-Meteo, with the National Weather Service as backup.</p>'
    )

    # --- thresholds ---
    kv = (
        '<h2 id="how-much">How much snow closes school in ' + E(name) + '?</h2>'
        f'<div class="answer" id="answer"><p>In {E(name)} it takes roughly <b>{fmt_in(s50)}</b> of new snow for the chance of a school closing to reach 50%, '
        f'and about <b>{fmt_in(s80)}</b> for 80%, for a plain overnight snowfall with no ice and no snow already on the ground. '
        f'Cold alone starts closing {E(name)} schools around <b>{cold}°F</b> wind chill.</p>'
        f'<p>Ice and leftover snowpack move those numbers sharply: 64% of the closures we tracked in 2025-26 followed less than an inch of new snow in the previous 48 hours.</p></div>'
        '<dl class="kv">'
        f'<dt>Region</dt><dd>{E(tier["label"])}</dd>'
        f'<dt>Snow for a 50% chance</dt><dd>{fmt_in(s50)}</dd>'
        f'<dt>Snow for an 80% chance</dt><dd>{fmt_in(s80)}</dd>'
        f'<dt>Cold-only closing</dt><dd>about {cold}°F wind chill</dd>'
        f'<dt>Basis</dt><dd>{basis}</dd>'
        '</dl>'
        f'<p>{E(TIER_TEXT[d["tier"]])}</p>'
    )

    # --- snowfall normals ---
    rows = "".join(f'<tr><td><a href="/?zip={c["zip"]}">{E(c["name"])}</a></td><td>{c["snow"]:g} in</td>'
                   f'<td>{"about " + ("%.0f" % max(1, c["snow"] / s50)) + "×" if c["snow"] >= s50 else "less than one"}</td></tr>' for c in cities)
    ratio_note = (f'{E(snowiest["name"])} averages about {snowiest["snow"]:g} inches a winter, {E(least["name"])} about {least["snow"]:g}'
                  if len(cities) > 1 else f'{E(big["name"])} averages about {big["snow"]:g} inches a winter')
    normals = (
        f'<h2 id="snowfall">How much snow {E(name)} actually gets</h2>'
        f'<p>{ratio_note}. The right-hand column shows how many times over the 50% threshold ({fmt_in(s50)}) each city\'s typical season adds up to — '
        f'a rough guide to how often the threshold is in play, not to how often schools close.</p>'
        f'<div class="tw"><table><thead><tr><th>City</th><th>Average snowfall per winter</th><th>Seasons\' worth of 50% thresholds</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<p class="note">Snowfall figures are rounded NOAA 1991-2020 climate normals for the nearest reporting station.</p>'
        f'<h2 id="season">When {E(name)} snow days happen</h2><p>{E(SEASON[d["tier"]])}</p>'
    )

    # --- 2025-26 table (tracked states only) ---
    hist = f'<h2 id="2025-26">What happened in {E(name)} in 2025-26</h2>{table}' if tracked else ""

    # --- districts & announcements ---
    dl = "".join(f"<li>{E(x)}</li>" for x in d["districts"])
    al = "".join(f"<li>{E(x)}</li>" for x in d["announce"])
    where = (
        f'<h2 id="closings">Where {E(name)} school closings are announced</h2>'
        f'<p>Closures are decided district by district. The largest districts in {E(name)} by enrollment, whose calls tend to set the tone for their neighbours:</p>'
        f'<ul>{dl}</ul>'
        f'<p>Official announcements come from the district itself — its website, app, text and email alerts — and are mirrored on local closings lists. In {E(name)} the lists most families check:</p>'
        f'<ul>{al}</ul>'
        f'<p class="note">This site forecasts the chance of a closure; it does not list closures. For whether your school is actually closed, use the district\'s own channel.</p>'
    )

    rules = f'<h2 id="makeup">Make-up days and remote days in {E(name)}</h2><p>{E(d["rules"])}</p><p class="note">Rules change and districts apply them differently; treat this as background, not policy.</p>'

    # --- FAQ ---
    faqs = [
        (f"Will schools close tomorrow in {name}?",
         f"The live board at the top of this page gives the chance for each major {name} city from the latest forecast; enter your ZIP code for your own neighbourhood. As a rule of thumb it takes about {fmt_in(s50)} of new overnight snow for a 50% chance in {name}, less if there is ice or snow already on the ground."),
        (f"How much snow does it take to cancel school in {name}?",
         f"About {fmt_in(s50)} of new snow for a 50% chance and {fmt_in(s80)} for 80%, for a plain overnight snowfall. Freezing rain closes {name} schools at almost any depth, and wind chill around {cold}°F can close them with no snow at all."),
        (f"Which {name} city gets the most snow?",
         (f"Of the cities on this page, {snowiest['name']} averages the most at roughly {snowiest['snow']:g} inches a winter, and {least['name']} the least at about {least['snow']:g} inches."
          if len(cities) > 1 else f"{big['name']} averages roughly {big['snow']:g} inches a winter.")),
        (f"Where are {name} school closings announced?",
         f"By each district on its own website and alerts, and on local closings lists such as {d['announce'][0]}. This site estimates the chance of a closure; it does not announce them."),
        (f"Does {name} make up snow days?",
         d["rules"]),
    ]
    faq_html = '<h2 id="faq">' + E(name) + ' snow day questions</h2>' + "".join(
        f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    # --- nearby states ---
    nb = [n for n in d["neighbors"] if n in STATES]
    nearby = ('<h2 id="nearby">Nearby states</h2><div class="chips">' +
              "".join(f'<a href="/states/{n.lower()}/">{E(STATES[n]["name"])}</a>' for n in nb) +
              '<a href="/states/">All states</a></div>') if nb else ""

    related = ('<nav class="related" aria-labelledby="rel-h"><h2 id="rel-h">Related pages</h2><ul>'
               '<li><a href="/">Snow day calculator</a></li><li><a href="/snow-day-tomorrow/">Chance of a snow day tomorrow</a></li>'
               '<li><a href="/school-closing-predictions/">School closing predictions</a></li><li><a href="/two-hour-delay/">Two-hour delays</a></li>'
               '<li><a href="/cold-day-school-closings/">Cold days and wind chill</a></li><li><a href="/2025-26-closures/">2025-26 closure data</a></li></ul></nav>')

    # --- schema ---
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#page", "url": url, "name": title, "description": desc,
               "inLanguage": "en-US", "dateModified": TODAY,
               "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE},
               "about": {"@type": "Place", "name": name},
               "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#answer", "h1"]}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "By state", "item": SITE + "/states/"},
        {"@type": "ListItem", "position": 3, "name": name, "item": url}]}
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": f"{name} Snow Day Calculator", "url": url,
              "applicationCategory": "UtilityApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
              "description": f"Live chance of a snow day tomorrow in {name}, by city, from the current forecast."}
    cities_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{name} cities on the live board",
                 "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["name"], "url": f"{SITE}/?zip={c['zip']}"} for i, c in enumerate(cities)]}

    sb_json = json.dumps([{k: c[k] for k in ("name", "zip", "lat", "lon", "st")} for c in cities], separators=(",", ":"))

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#1d5bb8">
<meta property="og:type" content="website"><meta property="og:site_name" content="Snow Day Forecaster">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/json" href="/api/states.json" title="Machine-readable state thresholds">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="preconnect" href="https://api.open-meteo.com">
{STYLE}
{EXTRA_CSS}
{jsonld([ORG, page_ld, crumb_ld, app_ld, faq_ld, cities_ld])}
{COEF}
<script src="/assets/model.js" defer></script>
<script src="/assets/stateboard.js" defer></script>
</head>
<body>
{HEADER}
<main class="wrap"><p class="crumb"><a href="/">Home</a> / <a href="/states/">By state</a> / {E(name)}</p>
<h1>{E(h1)}</h1>
<p class="lede">{E(lede)}</p>
<script id="sb-cities" type="application/json">{sb_json}</script>
{board}
{kv}
{normals}
{hist}
{where}
{rules}
{faq_html}
{nearby}
{related}
</main>
{FOOTER}
</body>
</html>
"""
    out = os.path.join(ROOT, "states", code.lower(), "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    return dict(code=code, name=name, url=url, tier=d["tier"], s50=s50, s80=s80, cold=cold, tracked=tracked,
                cities=[dict(name=c["name"], zip=c["zip"], avg_snowfall_in=c["snow"]) for c in cities])

# ---------- hub page ----------
ORDER = ["north", "northeast", "midwest", "midatlantic", "south_border", "south"]
def build_hub(summary):
    p = os.path.join(ROOT, "states", "index.html")
    s = open(p, encoding="utf-8").read()
    groups = []
    for t in ORDER:
        items = [x for x in summary if x["tier"] == t]
        items.sort(key=lambda x: x["name"])
        if not items: continue
        cards = "".join(f'<a href="/states/{x["code"].lower()}/"><b>{E(x["name"])}</b><span>{x["s50"]:g} in for a 50% chance{" · tracked" if x["tracked"] else ""}</span></a>' for x in items)
        groups.append(f'<h3>{E(TIERS[t]["label"])}</h3><div class="cards">{cards}</div>')
    new_block = "<h2>States</h2>" + "".join(groups)
    s = re.sub(r"<h2>States</h2>.*?(?=<p class=\"note\">States without)", new_block, s, flags=re.S)
    s = s.replace("Pick your state below for its threshold and the districts we track there.",
                  "Pick your state below for its threshold, a live board of tomorrow's chances in its major cities, and where closings are announced.")
    s = re.sub(r'"dateModified":"\d{4}-\d{2}-\d{2}"', f'"dateModified":"{TODAY}"', s)
    open(p, "w", encoding="utf-8").write(s)

# ---------- sitemap ----------
def update_sitemap(summary):
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<url><loc>https://www\.snowdayforecaster\.com/states/[a-z]{2}/</loc>.*?</url>\s*", "", s, flags=re.S)
    entries = "".join(f"<url><loc>{x['url']}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>\n" for x in summary)
    s = s.replace("</urlset>", entries + "</urlset>")
    s = re.sub(r"(<loc>https://www\.snowdayforecaster\.com/states/</loc><lastmod>)[^<]+", r"\g<1>" + TODAY, s)
    open(p, "w", encoding="utf-8").write(s)

def main():
    summary = [build_state(c, d) for c, d in STATES.items()]
    build_hub(summary)
    update_sitemap(summary)
    api = {"name": "Snow Day Forecaster — state thresholds", "url": SITE + "/states/", "updated": TODAY, "license": "CC BY 4.0",
           "attribution": "Snow Day Forecaster (https://www.snowdayforecaster.com)",
           "note": "New snow (inches, plain overnight snowfall, no ice, no existing pack) needed for a 50% / 80% chance that a school district closes; cold-only threshold is wind chill °F. Regional model; see /methodology/.",
           "regions": {k: v for k, v in TIERS.items()}, "states": summary}
    json.dump(api, open(os.path.join(ROOT, "api", "states.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"built {len(summary)} state pages, hub, sitemap, api/states.json")

if __name__ == "__main__":
    main()
