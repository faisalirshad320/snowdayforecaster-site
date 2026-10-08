#!/usr/bin/env python3
"""Build the embeddable widget: /embed/ (the calculator served inside an iframe),
/embed.js (loader the host site pastes — injects the iframe AND a backlink anchor into
the host page's own DOM), and /add-widget/ (the info + copy-paste page).

Reuses the published model (assets/model.js + the inline COEF from the homepage) so the
widget behaves exactly like the site's live board.

Run from repo root:  python3 build-embed/build_embed.py
"""
import os, re, json, html, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.snowdayforecaster.com"
TODAY = datetime.date.today().isoformat()
E = html.escape

home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
STYLE = home[home.find("<style>"):home.find("</style>") + 8]
HEADER = home[home.find("<header"):home.find("</header>") + 9]
FOOTER = home[home.find("<footer"):home.find("</footer>") + 9]
COEF = re.search(r"<script>window\.SDF_COEF=.*?</script>", home, re.S).group(0)
ORG = json.loads(home[home.find('<script type="application/ld+json">') + 35:home.find("</script>", home.find('<script type="application/ld+json">'))])[0]

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"

# ---------------- /embed/ : the in-iframe calculator ----------------
EMBED_CSS = """<style>
html,body{margin:0}body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--sans,system-ui,sans-serif);padding:14px}
.w{max-width:420px;margin:0 auto}
.w h2{font-size:17px;margin:0 0 4px}.w p.sub{margin:0 0 12px;color:var(--muted);font-size:13px}
.w form{display:flex;gap:8px}
.w input{flex:1;min-width:0;font:inherit;font-size:18px;letter-spacing:.06em;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);min-height:46px}
.w button{background:var(--accent);color:var(--accent-ink);border:0;border-radius:10px;padding:0 16px;font-weight:700;min-height:46px;cursor:pointer}
#r{margin:14px 0 0;min-height:1.2em}
.big{font-size:40px;font-weight:800;line-height:1.05}
.band{font-size:15px;font-weight:600;margin-left:6px}
.meta{color:var(--muted);font-size:13px;margin:4px 0 0}
.next{margin:10px 0 0;font-size:14px;color:var(--muted)}
.cr{margin:14px 0 0;font-size:12px;color:var(--muted)}.cr a{color:var(--accent);font-weight:600;text-decoration:none}
.err{color:#b4232a}
.b5{color:#0b7a34}.b4{color:#1d8a3f}.b3{color:#b8860b}.b2{color:#c06b00}.b1{color:#7a5cc0}.b0{color:var(--muted)}
</style>"""

EMBED_JS = """<script>
document.addEventListener("DOMContentLoaded",function(){
  if(!window.SnowModel||!window.SDF_COEF){return;}
  var M=window.SnowModel.load(window.SDF_COEF);
  var FC="https://api.open-meteo.com/v1/forecast";
  var f=document.getElementById("f"),z=document.getElementById("z"),r=document.getElementById("r");
  function post(){try{parent.postMessage({sdf:1,h:document.body.scrollHeight},"*");}catch(e){}}
  new ResizeObserver(post).observe(document.body);
  function band(p){if(p>=.9)return["Almost certain","b5"];if(p>=.7)return["Very likely","b4"];if(p>=.5)return["Likely","b3"];if(p>=.3)return["Possible","b2"];if(p>=.1)return["Unlikely","b1"];return["Very unlikely","b0"];}
  function pct(p){return Math.min(99,Math.max(1,Math.round(p*100)));}
  function lookup(zip){var sh=zip.slice(0,2);return fetch("/zip/"+sh+".json").then(function(x){return x.json();}).then(function(j){return j[zip];});}
  function wx(lat,lon){var q="?latitude="+lat.toFixed(3)+"&longitude="+lon.toFixed(3)+"&daily=snowfall_sum,precipitation_sum,temperature_2m_max,apparent_temperature_min&past_days=7&forecast_days=5&timezone=auto&temperature_unit=fahrenheit&precipitation_unit=inch";
    return fetch(FC+q).then(function(x){if(!x.ok)throw 0;return x.json();});}
  f.addEventListener("submit",function(e){
    e.preventDefault();
    var zip=(z.value||"").trim();
    if(!/^[0-9]{5}$/.test(zip)){r.innerHTML='<p class="err">Enter a 5-digit US ZIP code.</p>';post();return;}
    r.innerHTML='<p class="meta">Checking the latest forecast…</p>';post();
    lookup(zip).then(function(e0){
      if(!e0){r.innerHTML='<p class="err">ZIP not found. Try a nearby ZIP.</p>';post();return;}
      var lat=e0[0],lon=e0[1],place=e0[2],st=e0[3];
      return wx(lat,lon).then(function(j){
        var d=j.daily,pack=M.packSeries(d),tier=M.tierFor(st,lat);
        var today=new Date().toLocaleDateString("en-CA"),i0=d.time.indexOf(today);if(i0<0)i0=d.time.length-5;
        var picks=[];
        for(var k=1;k<=4&&i0+k<d.time.length;k++){var i=i0+k,wd=new Date(d.time[i]+"T12:00:00").getDay();if(wd===0||wd===6)continue;
          var ft=M.features(d,i,pack);picks.push({iso:d.time[i],p:M.probability(ft,tier),f:ft});if(picks.length>=2)break;}
        if(!picks.length){r.innerHTML='<p class="meta">No school day in range to forecast.</p>';post();return;}
        var a=picks[0],bd=band(a.p),dt=new Date(a.iso+"T12:00:00");
        var lbl=dt.toLocaleDateString("en-US",{weekday:"long",month:"short",day:"numeric"});
        var h='<div><span class="big '+bd[1]+'">'+pct(a.p)+'%</span><span class="band '+bd[1]+'">'+bd[0]+'</span></div>';
        h+='<p class="meta">chance of a snow day '+lbl+' in '+(place?place:zip)+(st?", "+st:"")+' — '+M.driver(a.f)+'.</p>';
        if(picks[1]){var b=picks[1],d2=new Date(picks[1].iso+"T12:00:00");h+='<p class="next">Next school day ('+d2.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"})+'): <b>'+pct(b.p)+'%</b></p>';}
        h+='<p class="cr">Forecast by <a href="'+location.origin+'/?zip='+zip+'" target="_blank" rel="noopener">Snow Day Forecaster</a> · not an official closure</p>';
        r.innerHTML=h;post();
      });
    }).catch(function(){r.innerHTML='<p class="err">Forecast service didn\\'t answer. Try again in a minute.</p>';post();});
  });
  post();
});
</script>"""

def build_embed():
    url = SITE + "/embed/"
    title = "Snow Day Calculator widget"
    desc = "Embeddable snow day calculator — enter a ZIP for tomorrow's chance of a school closing."
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Snow Day Calculator widget", "url": url,
              "applicationCategory": "UtilityApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{SITE}/add-widget/">
<link rel="preconnect" href="https://api.open-meteo.com">
{STYLE}
{EMBED_CSS}
{jsonld([app_ld])}
{COEF}
<script src="/assets/model.js" defer></script>
{EMBED_JS}
</head>
<body>
<div class="w">
<h2>Will there be a snow day?</h2>
<p class="sub">Enter your ZIP for tomorrow's chance of a school closing.</p>
<form id="f"><input id="z" inputmode="numeric" pattern="[0-9]{{5}}" maxlength="5" placeholder="ZIP code" aria-label="ZIP code" required><button type="submit">Check</button></form>
<div id="r"></div>
</div>
</body>
</html>
"""
    os.makedirs(os.path.join(ROOT, "embed"), exist_ok=True)
    open(os.path.join(ROOT, "embed", "index.html"), "w", encoding="utf-8").write(page)

# ---------------- /embed.js : the loader the host site pastes ----------------
def build_loader():
    js = """/* Snow Day Forecaster embeddable widget loader.
   Paste on your page:  <div class="sdf-widget"></div>
                        <script src="https://www.snowdayforecaster.com/embed.js" async></script>
   It inserts the calculator and a visible credit link back to Snow Day Forecaster. */
(function(){
  var SITE="https://www.snowdayforecaster.com";
  function init(){
    var nodes=document.querySelectorAll(".sdf-widget:not([data-sdf-done])");
    nodes.forEach(function(el){
      el.setAttribute("data-sdf-done","1");
      var f=document.createElement("iframe");
      f.src=SITE+"/embed/";f.title="Snow Day Calculator";f.loading="lazy";
      f.setAttribute("scrolling","no");
      f.style.cssText="width:100%;max-width:440px;height:230px;border:1px solid #e2e8f0;border-radius:12px;background:#fff;display:block";
      el.appendChild(f);
      var cr=document.createElement("div");
      cr.style.cssText="max-width:440px;font:13px/1.4 system-ui,sans-serif;color:#64748b;margin:6px 0 0";
      cr.innerHTML='Snow day odds by <a href="'+SITE+'/" rel="noopener" style="color:#1d5bb8;font-weight:600">Snow Day Forecaster</a>';
      el.appendChild(cr);
    });
  }
  window.addEventListener("message",function(e){
    if(!e.data||e.data.sdf!==1)return;
    document.querySelectorAll(".sdf-widget iframe").forEach(function(f){
      if(f.contentWindow===e.source&&e.data.h){f.style.height=(e.data.h+2)+"px";}
    });
  });
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
"""
    open(os.path.join(ROOT, "embed.js"), "w", encoding="utf-8").write(js)

# ---------------- /add-widget/ : the info + copy-paste page ----------------
def esc_snippet(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_info():
    url = SITE + "/add-widget/"
    title = "Add a free snow day calculator widget to your site"
    desc = "Embed the Snow Day Forecaster calculator on your school, district, PTA or weather site in one line — visitors get tomorrow's snow day chance for their own ZIP. Free."
    iframe_snippet = ('<iframe src="https://www.snowdayforecaster.com/embed/" title="Snow Day Calculator" '
                      'style="width:100%;max-width:440px;height:230px;border:1px solid #e2e8f0;border-radius:12px" loading="lazy"></iframe>\n'
                      '<p style="font:13px sans-serif">Snow day odds by <a href="https://www.snowdayforecaster.com/">Snow Day Forecaster</a></p>')
    script_snippet = ('<div class="sdf-widget"></div>\n'
                      '<script src="https://www.snowdayforecaster.com/embed.js" async></script>')
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
               "description": desc, "inLanguage": "en-US", "dateModified": TODAY,
               "isPartOf": {"@type": "WebSite", "name": "Snow Day Forecaster", "url": SITE}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Add the widget", "item": url}]}
    howto_ld = {"@context": "https://schema.org", "@type": "HowTo", "name": "Add the snow day calculator to your website",
                "step": [{"@type": "HowToStep", "position": 1, "text": "Copy the one-line embed code below."},
                         {"@type": "HowToStep", "position": 2, "text": "Paste it into your page's HTML where you want the calculator to appear."},
                         {"@type": "HowToStep", "position": 3, "text": "Save — the calculator loads automatically with a credit link back to Snow Day Forecaster."}]}
    body = f"""<main class="wrap"><p class="crumb"><a href="/">Home</a> / Add the widget</p>
<h1>Add the snow day calculator to your site</h1>
<p class="lede">Drop the Snow Day Forecaster calculator onto your school, district, PTA, classroom or weather page. Visitors type their ZIP and get tomorrow's chance of a school closing from the live forecast — free, no sign-up, works on any site.</p>

<h2 id="preview">Live preview</h2>
<div class="sdf-widget"></div>
<script src="/embed.js" async></script>

<h2 id="get">Get the code</h2>
<p><b>Option 1 — one line (works anywhere HTML is allowed).</b> Paste this where you want the widget:</p>
<pre class="code"><code>{esc_snippet(iframe_snippet)}</code></pre>
<p><b>Option 2 — auto-resizing (recommended).</b> This version grows to fit the result and adds the credit link for you:</p>
<pre class="code"><code>{esc_snippet(script_snippet)}</code></pre>

<h2 id="notes">Good to know</h2>
<ul>
<li>Free to use on any non-commercial or commercial site. Please keep the “Snow Day Forecaster” credit link — that is all we ask in return.</li>
<li>The widget shows a <b>probability from the weather</b>, not an official closure. Your district always makes the final call.</li>
<li>It runs the same published model used across this site, on the latest Open-Meteo forecast, and caches results in the visitor's browser for 30 minutes.</li>
<li>Questions or want a custom size? Email <a href="mailto:editor@snowdayforecaster.com">editor@snowdayforecaster.com</a>.</li>
</ul>

<nav class="related" aria-labelledby="rel-h"><h2 id="rel-h">Related pages</h2><ul>
<li><a href="/">Snow day calculator</a></li><li><a href="/snow-day-questions/">Snow day questions answered</a></li>
<li><a href="/states/">Snow day by state</a></li><li><a href="/cities/">Snow day by city</a></li>
<li><a href="/methodology/">How the model works</a></li></ul></nav>
</main>"""
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
{STYLE}
<style>.code{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;overflow:auto;font-size:13px;white-space:pre-wrap;word-break:break-word}}</style>
{jsonld([ORG, page_ld, crumb_ld, howto_ld])}
</head>
<body>
{HEADER}
{body}
{FOOTER}
</body>
</html>
"""
    os.makedirs(os.path.join(ROOT, "add-widget"), exist_ok=True)
    open(os.path.join(ROOT, "add-widget", "index.html"), "w", encoding="utf-8").write(page)

def update_sitemap():
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<url><loc>https://www\.snowdayforecaster\.com/add-widget/</loc>.*?</url>\s*", "", s, flags=re.S)
    entry = f'<url><loc>{SITE}/add-widget/</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
    s = s.replace("</urlset>", entry + "</urlset>")
    open(p, "w", encoding="utf-8").write(s)

if __name__ == "__main__":
    build_embed(); build_loader(); build_info(); update_sitemap()
    print("built /embed/, /embed.js, /add-widget/, sitemap entry")
