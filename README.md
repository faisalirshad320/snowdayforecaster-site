# Snow Day Forecaster (www.snowdayforecaster.com)

A static site: no database and no server code. The contents of `site/` are the web root.

Live at <https://www.snowdayforecaster.com>. Deployed from this repository's `main` branch
via Cloudways → Application → Deployment via GIT → **Pull**.

## Folders

- `site/` — the website (this is what gets deployed). Pages, `assets/` (model.js, app.js,
  coefficients.json), `api/summary.json`, `llms.txt`, `zip/` (ZIP lookup shards), `.htaccess`,
  sitemap, robots, icons.
- `model/` — back-test (`backtest.py`), closure ground truth (`closures.py`, `sources.py`),
  results (`results.json`, `scored_days.json`), exported coefficients.
- `weather/` — archived daily weather for the 20 test cities.
- `build/` — `build.py` regenerates `site/`; `clusters.py` holds the keyword clusters, topical
  map, state list and glossary; `parity.js` checks the JS model against Python; `shots.py` runs
  the browser test; `serve.js` is a local server.
- `GATES.md` — results of the three pre-build gates, the newsroom list and the pitch.

## Site structure

The page set follows the keyword clustering in `build/clusters.py`. Each cluster is one page,
each page opens with an answer block, and `LINKS` defines the internal linking.

| Page | Cluster head |
| --- | --- |
| `/` | snow day calculator (pillar, tool) |
| `/snow-day-tomorrow/` | chance of a snow day tomorrow |
| `/school-closing-predictions/` | school closing predictions |
| `/two-hour-delay/` | two hour delay |
| `/cold-day-school-closings/` | cold day / wind chill |
| `/lake-effect-snow/` | lake effect snow |
| `/how-to-get-a-snow-day/` | snow day superstitions |
| `/snow-day-activities/` | snow day activities |
| `/glossary/` | vocabulary (DefinedTermSet) |
| `/states/` + 23 state pages | snow day chances by state (pillar, local) |
| `/methodology/` | snow day calculator accuracy |
| `/2025-26-closures/` | the closure dataset |

### For AI crawlers and answer engines

- `robots.txt` names and allows the major AI crawlers explicitly (GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended, CCBot and others). Only `/zip/` is disallowed — it is
  machine data, not content.
- `llms.txt` is a plain-text map of the site with the headline figures and attribution terms.
- `api/summary.json` carries the same figures as JSON, so a tool can take them without
  parsing HTML.
- Every page carries `WebPage` schema with a `speakable` selector pointing at the answer
  block, plus page-specific `FAQPage`, `HowTo`, `Dataset`, `DefinedTermSet`, `ItemList`,
  `BreadcrumbList` and `Organization` as appropriate.

## State pages

`build-states/build_states.py` regenerates every `/states/<xx>/` page, the `/states/` hub, `api/states.json`
and the state entries in `sitemap.xml` from `build-states/states_data.py` (cities by ZIP, NOAA snowfall
normals, largest districts, closing-announcement outlets, make-up-day rules). Each state page carries a
live board (`assets/stateboard.js`) that runs the published model for its major cities. Edit the data file,
run the script from the repo root, commit.

## Deploying an update

```
python3 build/build.py               # regenerate site/
node build/parity.js                 # must print max diff < 1e-9
python3 build/shots.py               # browser test, expects no console errors
```

Then copy `site/` into the deploy repo, commit, push to `main`, and press **Pull** in
Cloudways (Application → Deployment via GIT). Nginx serves static files directly, so
`.htaccess` headers are not applied; the rewrite rules are handled at the server level and
the security headers would need an Nginx rule to take effect.

After deploying, purge Varnish so the new HTML is served:

```
curl -X PURGE http://127.0.0.1:8080/ -H 'Host: www.snowdayforecaster.com'
```

## Before you monetize

- **Open-Meteo licence:** the free API is for non-commercial use. Before switching ads on,
  buy an Open-Meteo API plan, then at the top of `site/assets/app.js` set
  `CFG.forecast` to `https://customer-api.open-meteo.com/v1/forecast` and `CFG.apikey` to the
  key. The NWS fallback is public domain and free for commercial use.
- Update `/privacy/` before adding analytics or ads.

## Rebuild after data changes

```
cd build && npm install              # zipcodes, lighthouse, playwright
python3 ../model/backtest.py         # re-run the back-test after changing data or features
python3 build.py
```
