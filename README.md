# Snow Day Forecaster (www.snowdayforecaster.com)

A static site: no database and no server code. **The repository root is the web root** — every
folder with an `index.html` is a page.

Live at <https://www.snowdayforecaster.com> on Cloudways (app 6699258, Lightning stack = Nginx
only, so `.htaccess` is **not** read; redirects and response headers live in Cloudways →
Application → Web rules).

## Folders

- Pages: `index.html` (homepage, hand-built), `states/`, `cities/`, `is-there-school-on/`,
  `snow-day-questions/`, `add-widget/`, `embed/` and the hand-built topic pages
  (`snow-day-tomorrow/`, `two-hour-delay/`, `methodology/`, `2025-26-closures/`, …).
- `assets/` — `model.js`, `app.js`, `stateboard.js`, coefficients. `zip/` — ZIP → lat/lon shards
  (100 files, all US ZIP prefixes). `api/` — `summary.json`, `states.json`, `cities.json`.
- Builders (Python 3, no dependencies), run from the repo root:
  - `build-states/build_states.py` + `states_data.py` → `/states/<xx>/`, `/states/` cards, `api/states.json`
  - `build-cities/build_cities.py` + `cities_data.py` → `/cities/…`, `/snow-day-questions/`, `api/cities.json`
  - `build-holidays/build_holidays.py` + `holiday_closures.py` → `/is-there-school-on/…`
  - `build-embed/build_embed.py` → `/embed/`, `/embed.js`, `/add-widget/`
  - Each builder rewrites only its own entries in `sitemap.xml`.
- `build-cities/pagedates.py` + `page_dates.json` — real `datePublished` / `dateModified` and
  sitemap `<lastmod>` for every generated page (see below).

Builders lift the page chrome (`<style>`, header, footer, Organization JSON-LD, model
coefficients) from the live `index.html`, so edit the homepage chrome first, then rebuild.

### Dates

A page's `dateModified` and its sitemap `<lastmod>` move only when its title, description or
`<main>` content changes (content hash in `page_dates.json`). `datePublished` is the date git
first saw the file. Commit `page_dates.json` with every rebuild. Never stamp today's date by hand.

### Holiday pages

Dates are computed from the holiday rules. `holiday_closures.py` holds the counted closures
(largest district per covered state, read from each district's published calendar, with the
retrieval date). Holiday titles carry the year of the next date, so **rebuild in the first week
of every January and after each holiday passes**, and refresh `holiday_closures.py` when the next
school year's calendars are published (spring).

## Site structure

The page set follows a keyword clustering (the original clustering script is not in this repo). Each cluster is one page,
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
python3 build-states/build_states.py
python3 build-cities/build_cities.py
python3 build-holidays/build_holidays.py
python3 build-embed/build_embed.py
git add -A && git commit
```

Then in Cloudways → Application → Deployment via GIT press **Pull** (or copy the changed files
to `~/applications/hydneyzttv/public_html/` over SFTP/SSH), and purge the cache: Cloudways →
Application → **Purge** (Varnish), or `curl -X PURGE http://127.0.0.1:8080/ -H 'Host: www.snowdayforecaster.com'`
on the server.

Security headers (HSTS, nosniff, Referrer-Policy) are set as Cloudways web rules. The CSP in
`.htaccess` is not applied: its `frame-ancestors 'self'` would block the embeddable widget on
other sites, so any CSP added later must exempt `/embed/`.

## Before you monetize

- **Open-Meteo licence:** the free API is for non-commercial use. Before switching ads on,
  buy an Open-Meteo API plan, then at the top of `assets/app.js` set
  `CFG.forecast` to `https://customer-api.open-meteo.com/v1/forecast` and `CFG.apikey` to the
  key. The NWS fallback is public domain and free for commercial use.
- Update `/privacy/` before adding analytics or ads.

## Model and back-test

The back-test, closure ground truth and weather archive that produced `assets/coefficients.json`
and `api/summary.json` (model version 2026-09-29, 20 districts, 2025-26 season) are **not in this
repository**. Until they are added, the model cannot be re-run from here; `/2025-26-closures/` is
last season's dataset and a 2026-27 dataset has not been started.
