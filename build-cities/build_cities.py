#!/usr/bin/env python3
"""Regenerate /cities/<slug>/index.html, /cities/index.html, /snow-day-questions/index.html,
/api/cities.json and the city/questions entries in sitemap.xml.

Metro pages reuse their state's thresholds (tier) from states_data and the same page chrome
(styles, header, footer, model script) lifted from the live homepage, so they match the rest
of the site and carry the same live forecast board.

Run from the repo root:  python3 build-cities/build_cities.py
"""
import json, os, re, sys, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "build-states"))
from cities_data import CITIES
from states_data import STATES, TIERS, TIER_TEXT, SEASON

ROOT = os.path.dirname(HERE)
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
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:12px 0}.cards a{text-decoration:none;border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--card);color:var(--ink);display:flex;flex-direction:column;gap:3px}.cards a:hover{border-color:var(--accent)}.cards b{font-size:16px}.cards span{font-size:13px;color:var(--muted)}
</style>"""

# ---------- zip shards for coordinates ----------
_shards = {}
def zip_info(z):
    sh = z[:2]
    if sh not in _shards:
        _shards[sh] = json.load(open(os.path.join(ROOT, "zip", sh + ".json")))
    e = _shards[sh][z]
    return dict(lat=e[0], lon=e[1], place=e[2], st=e[3])

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"

def fmt_in(x):
    return ("%g" % x) + (" inch" if x == 1 else " inches")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#1d5bb8">
<meta property="og:type" content="website"><meta property="og:site_name" content="Snow Day Forecaster">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{site}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/json" href="/api/cities.json" title="Machine-readable metro thresholds">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="preconnect" href="https://api.open-meteo.com">
{style}
{extra}
{ld}
{coef}
<script src="/assets/model.js" defer></script>
{board_js}
</head>
<body>
{header}
"""

# ---------- one metro page ----------
def build_city(slug, d):
    name, st = d["name"], d["state"]
    sname = STATES[st]["name"]
    tkey = STATES[st]["tier"]
    tier = TIERS[tkey]
    s50, s80, cold = tier["s50"], tier["s80"], tier["cold"]
    url = f"{SITE}/cities/{slug}/"

    locs = []
    for cname, z, snow in d["board"]:
        try:
            zi = zip_info(z)
        except KeyError:
            print(f"  ! {slug}: skipping {cname} {z} (not in zip shard)")
            continue
        locs.append(dict(name=cname, zip=z, lat=zi["lat"], lon=zi["lon"], st=st, snow=snow))
    if not locs:
        raise SystemExit(f"{slug}: no valid board ZIPs")
    snowiest = max(locs, key=lambda c: c["snow"])
    least = min(locs, key=lambda c: c["snow"])

    title = f"{name} Snow Day Calculator: Chance of a Snow Day Tomorrow"
    desc = (f"Will schools close tomorrow in {name}? A live snow day calculator for {name} and its suburbs "
            f"({', '.join(c['name'] for c in locs[1:4])}…), how much snow closes {name} schools, and where closings are announced.")
    h1 = f"Snow day chances in {name} tomorrow"
    lede = (f"A live snow day calculator for the {name} area: the chance school closes tomorrow across the metro, "
            f"how much snow it takes, and where {name} districts announce closings.")

    board = (
        f'<h2 id="live">Will schools close tomorrow in {E(name)}?</h2>'
        f'<p>The board runs the <a href="/methodology/">published model</a> on the latest forecast for {len(locs)} '
        f'places across metro {E(name)}. It is a probability from the weather, not an announcement — districts make '
        f'their own call, usually the night before or by about 5:30 a.m.</p>'
        f'<p class="sb-summary" id="sb-summary">Loading the latest forecast…</p>'
        f'<div id="stateboard" aria-live="polite"><p class="note">Loading tomorrow\'s chances…</p></div>'
        f'<form class="zipcta" action="/" method="get"><label for="zipcta" style="position:absolute;left:-9999px">ZIP code</label>'
        f'<input id="zipcta" name="zip" inputmode="numeric" pattern="[0-9]{{5}}" maxlength="5" placeholder="Your {E(name)} ZIP code" required>'
        f'<button type="submit">Check my ZIP</button></form>'
        f'<p class="note">Chances are cached for 30 minutes in your browser. Forecast: Open-Meteo, with the National Weather Service as backup.</p>'
    )

    how = (
        '<h2 id="how-much">How much snow closes school in ' + E(name) + '?</h2>'
        f'<div class="answer" id="answer"><p>In the {E(name)} area it takes roughly <b>{fmt_in(s50)}</b> of new snow for the '
        f'chance of a school closing to reach 50%, and about <b>{fmt_in(s80)}</b> for 80%, for a plain overnight snowfall with no '
        f'ice and no snow already down. Cold alone starts closing schools around <b>{cold}°F</b> wind chill.</p>'
        f'<p>{E(d["blurb"])}</p></div>'
        '<dl class="kv">'
        f'<dt>Metro</dt><dd>{E(name)}, {E(sname)}</dd>'
        f'<dt>Snow for a 50% chance</dt><dd>{fmt_in(s50)}</dd>'
        f'<dt>Snow for an 80% chance</dt><dd>{fmt_in(s80)}</dd>'
        f'<dt>Cold-only closing</dt><dd>about {cold}°F wind chill</dd>'
        '</dl>'
        f'<p>{E(TIER_TEXT[tkey])}</p>'
    )

    rows = "".join(f'<tr><td><a href="/?zip={c["zip"]}">{E(c["name"])}</a></td><td>{c["snow"]:g} in</td>'
                   f'<td>{"about " + ("%.0f" % max(1, c["snow"] / s50)) + "×" if c["snow"] >= s50 else "less than one"}</td></tr>' for c in locs)
    normals = (
        f'<h2 id="snowfall">How much snow the {E(name)} area gets</h2>'
        f'<p>{E(snowiest["name"])} averages about {snowiest["snow"]:g} inches a winter and {E(least["name"])} about '
        f'{least["snow"]:g}. The right-hand column shows how many times over the 50% threshold ({fmt_in(s50)}) each place\'s '
        f'typical season adds up to — a rough guide to how often the threshold is in play, not how often schools actually close.</p>'
        f'<div class="tw"><table><thead><tr><th>Place</th><th>Average snowfall per winter</th><th>Seasons\' worth of 50% thresholds</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<p class="note">Snowfall figures are rounded NOAA 1991-2020 climate normals for the nearest reporting station.</p>'
        f'<h2 id="season">When {E(name)} snow days happen</h2><p>{E(SEASON[tkey])}</p>'
    )

    dl = "".join(f"<li>{E(x)}</li>" for x in d["districts"])
    al = "".join(f"<li>{E(x)}</li>" for x in d["announce"])
    where = (
        f'<h2 id="closings">Where {E(name)} school closings are announced</h2>'
        f'<p>Closures are decided district by district. The largest districts in and around {E(name)}, whose calls tend to '
        f'set the tone for their neighbours:</p><ul>{dl}</ul>'
        f'<p>Official announcements come from the district itself — its website, app, text and email alerts — and are mirrored '
        f'on local closings lists. Around {E(name)} the lists most families check:</p><ul>{al}</ul>'
        f'<p class="note">This site forecasts the chance of a closure; it does not list closures. For whether your school is actually closed, use the district\'s own channel.</p>'
    )

    rules = f'<h2 id="makeup">Make-up days and remote days in {E(sname)}</h2><p>{E(STATES[st]["rules"])}</p><p class="note">Rules change and districts apply them differently; treat this as background, not policy.</p>'

    faqs = [
        (f"Will schools close tomorrow in {name}?",
         f"The live board at the top of this page gives the chance for {name} and its suburbs from the latest forecast; enter your ZIP for your own neighbourhood. As a rule of thumb it takes about {fmt_in(s50)} of new overnight snow for a 50% chance here, less if there is ice or snow already on the ground."),
        (f"How much snow does it take to cancel school in {name}?",
         f"About {fmt_in(s50)} of new snow for a 50% chance and {fmt_in(s80)} for 80%, for a plain overnight snowfall. Freezing rain closes schools at almost any depth, and wind chill around {cold}°F can close them with no snow at all."),
        (f"How does {name} decide on a snow day?",
         d["blurb"]),
        (f"Where are {name} school closings announced?",
         f"By each district on its own website and alerts, and on local lists such as {d['announce'][0]}. This site estimates the chance of a closure; it does not announce them."),
        (f"Which part of the {name} area gets the most snow?",
         f"Of the places on this page, {snowiest['name']} averages the most at roughly {snowiest['snow']:g} inches a winter and {least['name']} the least at about {least['snow']:g} inches."),
    ]
    faq_html = '<h2 id="faq">' + E(name) + ' snow day questions</h2>' + "".join(
        f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    nb = [n for n in d["neighbors"] if n in CITIES]
    chips = "".join(f'<a href="/cities/{n}/">{E(CITIES[n]["name"])}</a>' for n in nb)
    chips += f'<a href="/states/{st.lower()}/">All of {E(sname)}</a><a href="/cities/">All cities</a>'
    nearby = f'<h2 id="nearby">Nearby metros</h2><div class="chips">{chips}</div>'

    related = ('<nav class="related" aria-labelledby="rel-h"><h2 id="rel-h">Related pages</h2><ul>'
               '<li><a href="/">Snow day calculator</a></li><li><a href="/snow-day-tomorrow/">Chance of a snow day tomorrow</a></li>'
               '<li><a href="/snow-day-questions/">Snow day questions answered</a></li>'
               f'<li><a href="/states/{st.lower()}/">{E(sname)} snow days</a></li>'
               '<li><a href="/two-hour-delay/">Two-hour delays</a></li><li><a href="/cold-day-school-closings/">Cold days and wind chill</a></li></ul></nav>')

    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#page", "url": url, "name": title, "description": desc,
               "inLanguage": "en-US", "dateModified": TODAY,
               "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE},
               "about": {"@type": "City", "name": name},
               "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#answer", "h1"]}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Cities", "item": SITE + "/cities/"},
        {"@type": "ListItem", "position": 3, "name": name, "item": url}]}
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": f"{name} Snow Day Calculator", "url": url,
              "applicationCategory": "UtilityApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
              "description": f"Live chance of a snow day tomorrow across metro {name}, from the current forecast."}
    locs_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{name}-area places on the live board",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["name"], "url": f"{SITE}/?zip={c['zip']}"} for i, c in enumerate(locs)]}

    sb_json = json.dumps([{k: c[k] for k in ("name", "zip", "lat", "lon", "st")} for c in locs], separators=(",", ":"))
    head = HEAD.format(title=E(title), desc=E(desc), url=url, site=SITE, style=STYLE, extra=EXTRA_CSS,
                       ld=jsonld([ORG, page_ld, crumb_ld, app_ld, faq_ld, locs_ld]), coef=COEF,
                       board_js='<script src="/assets/stateboard.js" defer></script>', header=HEADER)
    page = (head +
            f'<main class="wrap"><p class="crumb"><a href="/">Home</a> / <a href="/cities/">Cities</a> / {E(name)}</p>'
            f'<h1>{E(h1)}</h1><p class="lede">{E(lede)}</p>'
            f'<script id="sb-cities" type="application/json">{sb_json}</script>'
            f'{board}{how}{normals}{where}{rules}{faq_html}{nearby}{related}</main>\n{FOOTER}\n</body>\n</html>\n')

    out = os.path.join(ROOT, "cities", slug, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    return dict(slug=slug, name=name, state=st, url=url, kw=d["kw"], s50=s50, s80=s80, cold=cold,
                places=[dict(name=c["name"], zip=c["zip"], avg_snowfall_in=c["snow"]) for c in locs])

# ---------- cities hub ----------
def build_hub(summary):
    url = f"{SITE}/cities/"
    title = "Snow Day Calculator by City: Live Chances for Major US Metros"
    desc = "Live snow day chances for major US metros — New York City, Chicago, Denver, Boston, Detroit, Cleveland and more — with how much snow closes schools in each."
    by_state = {}
    for x in summary:
        by_state.setdefault(x["state"], []).append(x)
    groups = []
    for st in sorted(by_state, key=lambda s: STATES[s]["name"]):
        items = sorted(by_state[st], key=lambda x: x["name"])
        cards = "".join(f'<a href="/cities/{x["slug"]}/"><b>{E(x["name"])}</b><span>{x["s50"]:g} in for a 50% chance</span></a>' for x in items)
        groups.append(f'<h3>{E(STATES[st]["name"])}</h3><div class="cards">{cards}</div>')
    page_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "@id": url + "#page", "url": url,
               "name": title, "description": desc, "inLanguage": "en-US", "dateModified": TODAY,
               "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Cities", "item": url}]}
    head = HEAD.format(title=E(title), desc=E(desc), url=url, site=SITE, style=STYLE, extra=EXTRA_CSS,
                       ld=jsonld([ORG, page_ld, crumb_ld]), coef=COEF, board_js="", header=HEADER)
    page = (head +
            f'<main class="wrap"><p class="crumb"><a href="/">Home</a> / Cities</p>'
            f'<h1>Snow day chances by city</h1>'
            f'<p class="lede">Pick a metro for a live board of tomorrow\'s snow day chances across the area, how much snow closes its schools, and where closings are announced. Searching for your state instead? See <a href="/states/">snow days by state</a>.</p>'
            + "".join(groups) +
            '<p class="note">Each metro board runs the same published model used across the site on the current forecast for a cluster of places in the area.</p>'
            '</main>\n' + FOOTER + '\n</body>\n</html>\n')
    os.makedirs(os.path.join(ROOT, "cities"), exist_ok=True)
    open(os.path.join(ROOT, "cities", "index.html"), "w", encoding="utf-8").write(page)

# ---------- snow-day-questions AEO hub ----------
QUESTIONS = [
    ("What are the chances of a snow day tomorrow?",
     "Enter your ZIP code in the snow day calculator and it gives tomorrow's chance as a percentage, read straight from the latest forecast. As a rough national guide, 3–4 inches of fresh overnight snow puts most districts near a coin-flip, and more cold, ice or existing snowpack pushes the odds higher."),
    ("How is the chance of a snow day calculated?",
     "The model combines the forecast snowfall, the overnight low and wind chill, freezing rain, how much snow is already on the ground, and whether tomorrow is a school day, then weights them for your region. It was tuned against 20 US districts' real 2025-26 closures — see the methodology page for the full basis."),
    ("What snow day percentage means school will probably close?",
     "Above roughly 70% a closure is likely and above 90% it is nearly certain, though districts still differ. Between about 30% and 60% the call is genuinely uncertain and often comes down to timing, road crews and ice rather than snow depth."),
    ("When is the next snow day?",
     "There is no fixed schedule — a snow day happens when a storm lines up with a school night. The calculator looks four school days ahead, so the honest answer is to check the next-few-days view whenever snow is in your forecast."),
    ("Is it a snow day today?",
     "This site forecasts the chance of a closure; it does not announce closures. For whether school is actually closed today, check your district's website, app or text alerts, or the local TV closings list — those are the only official sources."),
    ("Is tomorrow a snow day?",
     "Type your ZIP into the calculator for tomorrow's probability from the current forecast. Remember it is a forecast of the odds, not a decision — your district makes the final call, usually the night before or by about 5:30 a.m."),
    ("How much snow is needed to cancel school?",
     "For a plain overnight snowfall it takes roughly 3–6 inches for a 50% chance in much of the country, less in the South and more in snow-belt cities used to heavy snow. Ice is the big exception: freezing rain can close schools with almost no accumulation at all."),
    ("Can school be cancelled for cold with no snow?",
     "Yes. Many districts, especially in the Upper Midwest and Northeast, close or delay on extreme cold alone, typically when the wind chill falls to somewhere between about −20°F and −35°F. The calculator factors wind chill into the chance."),
    ("How accurate are snow day predictors?",
     "A good predictor is only as good as the weather forecast it runs on, so a day out it is fairly reliable and several days out it is a rough guide. It also cannot know local politics — some districts close quickly, others almost never do — which is why this model is tuned on real closure data rather than snowfall alone."),
    ("What is the difference between a snow day and a two-hour delay?",
     "A delay pushes the start time (usually by two hours) to let roads be treated and temperatures rise, while a snow day closes school entirely. Borderline forecasts often become a delay first, which is then upgraded to a closure if conditions worsen — see the two-hour-delay page for how that call is made."),
    ("Do snow days have to be made up?",
     "Usually yes — most states set a minimum number of instructional days or minutes, and districts build a few spare days into the calendar. Beyond those, extra days are added at the end of the year or an e-learning/remote day is used instead; the rules vary by state and are summarised on each state page."),
    ("Will there be a snow day on Monday?",
     "Pick any upcoming school day in the calculator's multi-day view and it shows that day's chance from the latest forecast. Early in the week the forecast is still firming up, so treat a weekend reading for Monday as provisional and check again the night before."),
]
def build_questions():
    url = f"{SITE}/snow-day-questions/"
    title = "Snow Day Questions, Answered: Chances, Percentages and How It Works"
    desc = "Clear answers to the most-asked snow day questions — what the chances are tomorrow, how the percentage is calculated, how much snow cancels school, and when the next snow day might be."
    answer_block = (f'<div class="answer" id="answer"><p>To find the chance of a snow day tomorrow, enter your ZIP code in the '
                    f'<a href="/">snow day calculator</a>: it reads the latest forecast and gives a percentage for the next four school days. '
                    f'As a rough guide, 3–4 inches of fresh overnight snow puts most districts near a 50% chance, with cold, ice and existing '
                    f'snowpack pushing the odds higher.</p></div>')
    qa_html = "".join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in QUESTIONS)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in QUESTIONS]}
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#page", "url": url, "name": title, "description": desc,
               "inLanguage": "en-US", "dateModified": TODAY, "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE},
               "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#answer", "h1"]}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Snow day questions", "item": url}]}
    head = HEAD.format(title=E(title), desc=E(desc), url=url, site=SITE, style=STYLE, extra=EXTRA_CSS,
                       ld=jsonld([ORG, page_ld, crumb_ld, faq_ld]), coef=COEF, board_js="", header=HEADER)
    related = ('<nav class="related" aria-labelledby="rel-h"><h2 id="rel-h">Related pages</h2><ul>'
               '<li><a href="/">Snow day calculator</a></li><li><a href="/snow-day-tomorrow/">Chance of a snow day tomorrow</a></li>'
               '<li><a href="/cities/">Snow day by city</a></li><li><a href="/states/">Snow day by state</a></li>'
               '<li><a href="/two-hour-delay/">Two-hour delays</a></li><li><a href="/methodology/">How the model works</a></li></ul></nav>')
    page = (head +
            f'<main class="wrap"><p class="crumb"><a href="/">Home</a> / Snow day questions</p>'
            f'<h1>Snow day questions, answered</h1>'
            f'<p class="lede">The questions people ask most about snow days — the odds tomorrow, what a snow day percentage means, how much snow cancels school, and how the forecast is worked out.</p>'
            f'{answer_block}<h2 id="faq">Common snow day questions</h2>{qa_html}{related}</main>\n{FOOTER}\n</body>\n</html>\n')
    os.makedirs(os.path.join(ROOT, "snow-day-questions"), exist_ok=True)
    open(os.path.join(ROOT, "snow-day-questions", "index.html"), "w", encoding="utf-8").write(page)

# ---------- sitemap + api + llms ----------
def update_sitemap(summary):
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<url><loc>https://www\.snowdayforecaster\.com/cities/[a-z-]*/?</loc>.*?</url>\s*", "", s, flags=re.S)
    s = re.sub(r"<url><loc>https://www\.snowdayforecaster\.com/snow-day-questions/</loc>.*?</url>\s*", "", s, flags=re.S)
    extra = f'<url><loc>{SITE}/cities/</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>\n'
    extra += f'<url><loc>{SITE}/snow-day-questions/</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
    extra += "".join(f"<url><loc>{x['url']}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>\n" for x in summary)
    s = s.replace("</urlset>", extra + "</urlset>")
    open(p, "w", encoding="utf-8").write(s)

def main():
    summary = [build_city(slug, d) for slug, d in CITIES.items()]
    build_hub(summary)
    build_questions()
    update_sitemap(summary)
    api = {"name": "Snow Day Forecaster — metro thresholds", "url": SITE + "/cities/", "updated": TODAY, "license": "CC BY 4.0",
           "attribution": "Snow Day Forecaster (https://www.snowdayforecaster.com)",
           "note": "New snow (inches, plain overnight snowfall) needed for a 50% / 80% chance a school district closes; cold-only threshold is wind chill °F. Metro figures inherit the state regional model; see /methodology/.",
           "cities": summary}
    json.dump(api, open(os.path.join(ROOT, "api", "cities.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"built {len(summary)} city pages, cities hub, questions hub, sitemap, api/cities.json")

if __name__ == "__main__":
    main()
