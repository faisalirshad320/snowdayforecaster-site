#!/usr/bin/env python3
"""Regenerate /is-there-school-on/<holiday>/ pages and the /is-there-school-on/ hub, plus their
entries in sitemap.xml. Page chrome is reused from build_cities (which lifts it from the live
homepage), so these pages match the rest of the site.

Dates are computed, never hand-typed. School-closing practice is described qualitatively
because it is set district by district; no percentages are claimed.

Run from the repo root:  python3 build-holidays/build_holidays.py
"""
import os, re, sys, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "build-cities"))
sys.path.insert(0, os.path.join(ROOT, "build-states"))
import build_cities as bc   # reuse HEAD, STYLE, HEADER, FOOTER, ORG, EXTRA_CSS, jsonld

E, SITE = bc.E, bc.SITE
TODAY = datetime.date.today()
D = datetime.date

# ---------------------------------------------------------------- date rules
def nth_weekday(y, m, wd, n):          # wd: Mon=0
    d = D(y, m, 1)
    d += datetime.timedelta(days=(wd - d.weekday()) % 7)
    return d + datetime.timedelta(weeks=n - 1)

def last_weekday(y, m, wd):
    d = D(y, m + 1, 1) - datetime.timedelta(days=1) if m < 12 else D(y, 12, 31)
    return d - datetime.timedelta(days=(d.weekday() - wd) % 7)

def easter(y):                          # anonymous Gregorian algorithm
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return D(y, month, day)

def observed(d):                        # federal fixed-date rule
    if d.weekday() == 5: return d - datetime.timedelta(days=1), "observed Friday"
    if d.weekday() == 6: return d + datetime.timedelta(days=1), "observed Monday"
    return d, ""

def election_day(y):                    # Tuesday after the first Monday in November
    return nth_weekday(y, 11, 0, 1) + datetime.timedelta(days=1)

# ---------------------------------------------------------------- holidays
# federal: True if one of the 11 US federal holidays (5 U.S.C. 6103)
H = [
 dict(slug="veterans-day", name="Veterans Day", federal=True,
      rule=lambda y: D(y, 11, 11), rule_text="November 11 every year",
      kw=["is there school on veterans day", "are schools closed on veterans day"],
      answer=("It depends on your district. Veterans Day is a federal holiday, so federal offices and post offices "
              "close, but it is one of the holidays where public schools are most divided: many districts close, while "
              "many others stay open and hold assemblies or lessons about military service instead."),
      practice=("Unlike Thanksgiving or Memorial Day, there is no near-universal pattern. Some states and many large "
                "districts close for the day; others keep students in class on the view that teaching about veterans is "
                "more useful than a day off. Districts that stay open often invite veterans to speak."),
      snow="Veterans Day falls before the main snow season in most of the country, so it is rarely used as a snow "
           "make-up day. Early-season lake-effect snow can still close schools around it in the Great Lakes snow belts."),
 dict(slug="thanksgiving", name="Thanksgiving", federal=True,
      rule=lambda y: nth_weekday(y, 11, 3, 4), rule_text="the fourth Thursday of November",
      kw=["is there school on thanksgiving", "thanksgiving break schools"],
      answer=("No. Public schools across the United States are closed on Thanksgiving Day. Almost all districts also "
              "close on the Friday after, and many give the Wednesday before off too, or the whole week."),
      practice=("Thanksgiving is the most consistently observed school holiday in the country. Where districts differ is "
                "the length of the break: two days (Thursday and Friday), three days (adding Wednesday), or a full week. "
                "The full-week break has become more common since 2020."),
      snow="The Thanksgiving week is when early-season storms start to matter in the northern states. A storm on the "
           "Monday or Tuesday before the break can turn a shortened week into a closed one."),
 dict(slug="mlk-day", name="Martin Luther King Jr. Day", short="MLK Day", federal=True,
      rule=lambda y: nth_weekday(y, 1, 0, 3), rule_text="the third Monday of January",
      kw=["is there school on mlk day", "are schools closed on mlk day", "is there school on martin luther king day"],
      answer=("In most districts, no. Martin Luther King Jr. Day is a federal holiday and the large majority of US public "
              "school districts close for it. A smaller number stay open, and some use it as a scheduled snow make-up day."),
      practice=("Most large urban and suburban districts close for MLK Day. Where a district has "
                "lost several days to winter weather, its calendar may name MLK Day as an emergency make-up day — check "
                "the district's published calendar for a line such as 'make-up day if needed'."),
      snow="MLK Day falls in the heart of winter, often during the coldest week of the year. A storm over the long weekend "
           "can extend the closure into Tuesday, and extreme wind chill is a common reason for that."),
 dict(slug="presidents-day", name="Presidents' Day", federal=True,
      rule=lambda y: nth_weekday(y, 2, 0, 3), rule_text="the third Monday of February (officially Washington's Birthday)",
      kw=["is there school on presidents day", "are schools closed on presidents day"],
      answer=("Usually not. Presidents' Day — officially Washington's Birthday — is a federal holiday and most public "
              "school districts close. In the Northeast many districts close for the whole week as a mid-winter break."),
      practice=("Presidents' Day is the holiday most often turned into a snow make-up day. Districts that have used up "
                "their built-in snow days frequently reclaim it, or reclaim days from the mid-winter break around it, so "
                "the answer in a snowy year can change after the calendar is printed."),
      snow="This is peak snow season across the northern half of the country. If your district has had a heavy winter, "
           "check for a calendar update in late January or early February before planning around the day off."),
 dict(slug="columbus-day", name="Columbus Day / Indigenous Peoples' Day", federal=True,
      rule=lambda y: nth_weekday(y, 10, 0, 2), rule_text="the second Monday of October",
      kw=["is there school on columbus day", "are schools closed on columbus day"],
      answer=("It depends on where you live. The second Monday of October is a federal holiday, but public schools are "
              "split: many districts stay open, while others close. Many states and cities now observe the day as "
              "Indigenous Peoples' Day, and some districts use it for teacher training with no students in school."),
      practice=("This is one of the least consistently observed school holidays. Districts that close often do so because "
                "the day is a state holiday or is paired with a fall break; districts that stay open treat it as a normal "
                "school day. A 'professional development' day with no classes is a common middle ground."),
      snow="Mid-October is before the snow season almost everywhere, so this holiday has nothing to do with snow days. "
           "It does fall during peak fall-break season in districts with a balanced calendar."),
 dict(slug="good-friday", name="Good Friday", federal=False,
      rule=lambda y: easter(y) - datetime.timedelta(days=2), rule_text="the Friday before Easter Sunday (date changes every year)",
      kw=["is there school on good friday", "are schools closed on good friday"],
      answer=("It varies. Good Friday is not a federal holiday, so there is no national pattern. Many districts close, "
              "often because spring break is scheduled around Easter, while many others are open."),
      practice=("Closure on Good Friday usually comes from the calendar rather than the day itself: a district that sets "
                "spring break around Easter will be closed, and one that fixes spring break to a set week in March may "
                "not be. A few states observe it as a state holiday."),
      snow="In the northern states, districts that ran out of snow days sometimes reclaim Good Friday or days of spring "
           "break as make-up days, so check for a revised calendar after a heavy winter."),
 dict(slug="memorial-day", name="Memorial Day", federal=True,
      rule=lambda y: last_weekday(y, 5, 0), rule_text="the last Monday of May",
      kw=["is there school on memorial day"],
      answer=("No. Memorial Day is a federal holiday and public schools are closed nationwide. In much of the South and "
              "West the school year has already ended by then."),
      practice=("Memorial Day is consistently observed. In districts where the school year runs into June, it is the last "
                "long weekend of the year, and snow make-up days are often added to the calendar after it."),
      snow="If your district had a heavy winter, the days after Memorial Day are where make-up days usually land, which "
           "is why the last day of school can move later in a snowy year."),
 dict(slug="labor-day", name="Labor Day", federal=True,
      rule=lambda y: nth_weekday(y, 9, 0, 1), rule_text="the first Monday of September",
      kw=["is there school on labor day"],
      answer=("No. Labor Day is a federal holiday and public schools are closed. In many districts — especially in the "
              "Northeast and Midwest — the school year does not start until after Labor Day."),
      practice=("Labor Day is observed everywhere. Whether school has already started depends on the region: much of the "
                "South and West starts in early or mid-August, while many northern districts start the day after Labor Day."),
      snow="Labor Day has no connection to snow days, but the start date it sets matters later: districts that start "
           "after Labor Day have less room in June to add make-up days."),
 dict(slug="juneteenth", name="Juneteenth", federal=True,
      rule=lambda y: D(y, 6, 19), rule_text="June 19 (a federal holiday since 2021)", observed=True,
      kw=["is there school on juneteenth"],
      answer=("Most students are already on summer break. Juneteenth became a federal holiday in 2021; districts still in "
              "session on June 19 increasingly close for it, but many have finished the school year by then."),
      practice=("Juneteenth is the newest federal holiday, and district calendars have been adding it since 2021. When "
                "June 19 falls on a weekend, the federal holiday is observed on the nearest weekday."),
      snow="In northern districts with heavy winters, snow make-up days can push the last day of school into the week of "
           "Juneteenth, which is when the question actually matters."),
 dict(slug="election-day", name="Election Day", federal=False,
      rule=election_day, rule_text="the Tuesday after the first Monday in November",
      kw=["is there school on election day"],
      answer=("In many districts, no — but it varies. Election Day is not a federal holiday. Many districts close or "
              "schedule a teacher-training day because their school buildings serve as polling places, while others stay "
              "open as normal."),
      practice=("The main driver is polling places. Schools are common polling locations, and some districts close to keep "
                "students out of crowded buildings; others keep classes running and close only part of the building. A "
                "few states make the general election day a state holiday."),
      snow="Election Day comes before the snow season in most of the country, so it is rarely tied to snow-day planning."),
]

def next_dates(h, n=3):
    out, y = [], TODAY.year - 1
    while len(out) < n:
        d = h["rule"](y)
        note = ""
        if h.get("observed"):
            d, note = observed(d)
        if d >= TODAY:
            out.append((d, note))
        y += 1
    return out

NYSE_CLOSED = {"thanksgiving", "mlk-day", "presidents-day", "good-friday", "memorial-day", "labor-day", "juneteenth"}

def closed_table(h):
    fed = h["federal"]
    rows = [
        ("Public schools", "Set by each district (see above)"),
        ("Federal government offices", "Closed" if fed else "Open"),
        ("US Postal Service (mail delivery and post offices)", "Closed" if fed else "Open"),
        ("Banks (Federal Reserve holiday schedule)", "Most closed" if fed else "Open"),
        ("Stock market (NYSE, Nasdaq)", "Closed" if h["slug"] in NYSE_CLOSED else "Open"),
    ]
    return ("<div class=\"tw\"><table><thead><tr><th>What</th><th>Status</th></tr></thead><tbody>"
            + "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows) + "</tbody></table></div>")

def fmt(d):
    return d.strftime("%A, %B ") + str(d.day) + d.strftime(", %Y")

# ---------------------------------------------------------------- one page
def build_page(h):
    dates = next_dates(h)
    nd, nnote = dates[0]
    url = f"{SITE}/is-there-school-on/{h['slug']}/"
    short = h.get("short") or h["name"].split(" / ")[0]
    title = f"Is There School on {short} {nd.year}? Closings Explained"
    if len(title) > 62:
        title = f"Is There School on {short} {nd.year}?"
    desc = (f"{short} {nd.year} is {fmt(nd)}. Whether schools close, how districts decide, and where to check "
            f"your district's calendar.")[:158]
    h1 = f"Is there school on {short}?"
    lede = f"{short} {nd.year} falls on {fmt(nd)}{' (' + nnote + ')' if nnote else ''}. Here is whether schools close, and why it differs between districts."

    rows = "".join(f"<tr><td>{d.year}</td><td>{fmt(d)}{' (' + n + ')' if n else ''}</td></tr>" for d, n in dates)
    status = ("a <b>federal holiday</b> (one of the eleven set by 5 U.S.C. 6103), so federal offices, post offices and "
              "most banks are closed" if h["federal"] else
              "<b>not a federal holiday</b>, so federal offices, post offices and banks are open as normal")

    body = (
        f'<div class="answer" id="answer"><p><b>Short answer:</b> {E(h["answer"])}</p></div>'
        '<dl class="kv">'
        f'<dt>Next date</dt><dd>{fmt(nd)}</dd>'
        f'<dt>Rule</dt><dd>{E(h["rule_text"])}</dd>'
        f'<dt>Federal holiday</dt><dd>{"Yes" if h["federal"] else "No"}</dd>'
        '</dl>'
        f'<h2 id="dates">When is {E(short)}?</h2>'
        f'<p>{E(short)} is {E(h["rule_text"])}. The next three dates:</p>'
        f'<div class="tw"><table><thead><tr><th>Year</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<h2 id="status">Is {E(short)} a federal holiday?</h2>'
        f'<p>{E(short)} is {status}. Federal status does not decide whether schools close, though: public school '
        'calendars are set by each district (and in some states by the state), so the same holiday can be a day off in '
        'one district and a normal school day in the next.</p>'
        f'<h2 id="closed">What else is closed on {E(short)}?</h2>{closed_table(h)}'
        '<p class="note">Federal offices, the Postal Service and Federal Reserve banks follow the federal holiday list; '
        'private businesses and individual banks set their own hours. Stock markets follow the NYSE holiday calendar.</p>'
        f'<h2 id="practice">How school districts handle {E(short)}</h2><p>{E(h["practice"])}</p>'
        f'<h2 id="snow">{E(short)} and snow days</h2><p>{E(h["snow"])}</p>'
        '<p>For a weather-driven closure on any day, the <a href="/">snow day calculator</a> gives the chance your '
        'district closes tomorrow from the latest forecast.</p>'
        '<h2 id="check">How to check your own district</h2>'
        '<ul><li><b>The district calendar</b> is the only authoritative source. Most districts publish it as a PDF on '
        'their website before the school year starts.</li>'
        '<li><b>Look for make-up-day notes.</b> Calendars often mark holidays that will be reclaimed if too many snow '
        'days are used.</li>'
        '<li><b>Private and charter schools</b> set their own calendars and often differ from the local public district.</li></ul>'
    )

    faqs = [
        (f"Is there school on {short} {nd.year}?", h["answer"]),
        (f"What date is {short} {nd.year}?", f"{short} {nd.year} is {fmt(nd)}{' (' + nnote + ')' if nnote else ''}. It falls on {h['rule_text']}."),
        (f"Is {short} a federal holiday?", ("Yes. It is one of the eleven federal holidays, so federal offices and post "
                                            "offices are closed. Schools follow their own district calendar.") if h["federal"]
                                            else "No. Federal offices, post offices and banks stay open. Schools follow their own district calendar."),
        (f"Can {short} become a snow make-up day?", h["snow"]),
    ]
    faq_html = '<h2 id="faq">Questions about school on ' + E(short) + '</h2>' + "".join(
        f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    others = [x for x in H if x["slug"] != h["slug"]]
    chips = "".join(f'<a href="/is-there-school-on/{x["slug"]}/">{E(x.get("short") or x["name"].split(" / ")[0])}</a>' for x in others)
    nav = f'<h2 id="other">Other school holidays</h2><div class="chips">{chips}<a href="/is-there-school-on/">All holidays</a></div>'
    related = ('<nav class="related" aria-labelledby="rel-h"><h2 id="rel-h">Related pages</h2><ul>'
               '<li><a href="/">Snow day calculator</a></li><li><a href="/snow-day-tomorrow/">Chance of a snow day tomorrow</a></li>'
               '<li><a href="/two-hour-delay/">Two-hour delays</a></li><li><a href="/cold-day-school-closings/">Cold days and wind chill</a></li>'
               '<li><a href="/states/">Snow days by state</a></li><li><a href="/cities/">Snow days by city</a></li></ul></nav>')

    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
               "description": desc, "inLanguage": "en-US", "dateModified": TODAY.isoformat(),
               "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE},
               "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#answer", "h1"]}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "School holidays", "item": SITE + "/is-there-school-on/"},
        {"@type": "ListItem", "position": 3, "name": short, "item": url}]}
    event_ld = {"@context": "https://schema.org", "@type": "Event", "name": f"{short} {nd.year}",
                "startDate": nd.isoformat(), "endDate": nd.isoformat(),
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "eventStatus": "https://schema.org/EventScheduled",
                "location": {"@type": "Country", "name": "United States"},
                "description": f"{short}: {h['rule_text']}."}

    head = bc.HEAD.format(title=E(title), desc=E(desc), url=url, site=SITE, style=bc.STYLE, extra=bc.EXTRA_CSS,
                          ld=bc.jsonld([bc.ORG, page_ld, crumb_ld, faq_ld, event_ld]), coef="", board_js="",
                          header=bc.HEADER)
    page = (head +
            f'<main class="wrap"><p class="crumb"><a href="/">Home</a> / <a href="/is-there-school-on/">School holidays</a> / {E(short)}</p>'
            f'<h1>{E(h1)}</h1><p class="lede">{E(lede)}</p>'
            f'{body}{faq_html}{nav}{related}</main>\n{bc.FOOTER}\n</body>\n</html>\n')
    out = os.path.join(ROOT, "is-there-school-on", h["slug"], "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    return dict(slug=h["slug"], name=short, url=url, next=nd.isoformat(), federal=h["federal"], kw=h["kw"])

# ---------------------------------------------------------------- hub
def build_hub(summary):
    url = f"{SITE}/is-there-school-on/"
    title = "Is There School Today? US School Holidays Calendar"
    desc = "Is there school on Veterans Day, Thanksgiving, MLK Day or Presidents' Day? Next dates, federal status and how districts decide."
    summary = sorted(summary, key=lambda x: x["next"])
    cards = "".join(
        f'<a href="/is-there-school-on/{x["slug"]}/"><b>{E(x["name"])}</b>'
        f'<span>{fmt(D.fromisoformat(x["next"]))}{" · federal" if x["federal"] else " · not federal"}</span></a>'
        for x in summary)
    body = ('<div class="answer" id="answer"><p>Whether there is school on a holiday is set by each school district, not '
            'by federal law. Thanksgiving, Memorial Day and Labor Day are closed almost everywhere; Veterans Day, '
            'Columbus Day, Good Friday and Election Day vary widely between districts. The pages below give the next '
            'date for each holiday and how districts usually treat it.</p></div>'
            f'<h2 id="upcoming">Upcoming school holidays</h2><div class="cards">{cards}</div>'
            '<h2 id="snow">Holidays and snow days</h2><p>Winter holidays — Martin Luther King Jr. Day and Presidents\' Day '
            'especially — are the ones most often reclaimed as snow make-up days after a heavy winter. For the chance '
            'of a weather closure tomorrow, use the <a href="/">snow day calculator</a>.</p>')
    page_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "@id": url + "#page", "url": url,
               "name": title, "description": desc, "inLanguage": "en-US", "dateModified": TODAY.isoformat(),
               "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE}}
    list_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "US school holidays",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["name"], "url": x["url"]}
                                   for i, x in enumerate(summary)]}
    head = bc.HEAD.format(title=E(title), desc=E(desc), url=url, site=SITE, style=bc.STYLE, extra=bc.EXTRA_CSS,
                          ld=bc.jsonld([bc.ORG, page_ld, list_ld]), coef="", board_js="", header=bc.HEADER)
    page = (head + '<main class="wrap"><p class="crumb"><a href="/">Home</a> / School holidays</p>'
            '<h1>Is there school today? US school holidays</h1>'
            '<p class="lede">The next date for every major school holiday, and whether districts usually close.</p>'
            f'{body}</main>\n{bc.FOOTER}\n</body>\n</html>\n')
    out = os.path.join(ROOT, "is-there-school-on", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- sitemap + llms
def update_sitemap(summary):
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<url><loc>https://www\.snowdayforecaster\.com/is-there-school-on/[a-z-]*/?</loc>.*?</url>\s*", "", s, flags=re.S)
    t = TODAY.isoformat()
    extra = f'<url><loc>{SITE}/is-there-school-on/</loc><lastmod>{t}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
    extra += "".join(f'<url><loc>{x["url"]}</loc><lastmod>{t}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' for x in summary)
    open(p, "w", encoding="utf-8").write(s.replace("</urlset>", extra + "</urlset>"))

def update_llms(summary):
    p = os.path.join(ROOT, "llms.txt")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"\n## School holidays\n.*?(?=\n## |\Z)", "\n", s, flags=re.S)
    block = ("\n## School holidays\n\n"
             f"- [Is there school today? US school holidays]({SITE}/is-there-school-on/): next date and district practice for each holiday.\n"
             + "".join(f"- [Is there school on {x['name']}?]({x['url']}): next date {x['next']}; "
                       f"{'federal holiday' if x['federal'] else 'not a federal holiday'}.\n" for x in summary))
    open(p, "w", encoding="utf-8").write(s.rstrip("\n") + "\n" + block)

def main():
    summary = [build_page(h) for h in H]
    build_hub(summary)
    update_sitemap(summary)
    update_llms(summary)
    print(f"built {len(summary)} holiday pages + hub, sitemap, llms.txt")

if __name__ == "__main__":
    main()
