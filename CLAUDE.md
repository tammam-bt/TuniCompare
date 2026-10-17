# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

TuniCompare scrapes gaming products (laptops, desktops, screens) from three Tunisian retailers — Tunisianet, Mytek, Scoop Gaming — matches identical products across them, and serves a Flask site showing the three prices side by side with the best one highlighted.

The data lives in a SQLite file, `tunicompare.db`, built from the CSVs in `Main/Products/` and **committed to the repo**. The app opens it read-only. The site is deployed on Vercel's free Hobby plan as project `tunicompare`, at https://tunicompare.vercel.app, from the GitHub repo `tammam-bt/TuniCompare`. Every push to `main` is a production deploy, and other branches get preview deploys. Hosting must stay free; paid services are off the table.

The CSVs as scraped in summer 2025 are the archive. Never edit them by hand. The git tag `data-2025-08` marks that snapshot, which is also the last Postgres/Render version of the project.

## Commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # requirements.txt is web-only, which is what Vercel installs

python -m Scripts.build_db            # rebuild tunicompare.db from the CSVs (deletes and recreates it)
python app.py                         # dev server on http://localhost:5000
pytest                                # full suite (~1 min: the build runs the real matching)
pytest tests/test_app.py::test_offset_past_end_is_empty   # single test
python Run.py                         # scrape all three sites, then build_db (scrapers are from 2025 and likely broken)
```

After changing the CSVs or the build/matching code, rerun `python -m Scripts.build_db` and commit the updated `tunicompare.db`. Vercel serves the committed file and does not build it.

Python 3.12+ is required, because the scripts reuse the same quote type inside f-strings. `.python-version` pins 3.12 for Vercel.

## Architecture

Data flows in one direction. The modules live in `Scripts/`, which is a namespace package (no `__init__.py`), so run things from the repo root.

1. **Scrapers** (`Tunisianet.py`, `Mytek.py`, `ScoopGaming.py`): requests + BeautifulSoup.
   - Each module has the same shape:
     - `normalize_text_*`
     - `get_specs_*`: regex extraction of CPU, RAM, GPU, storage and screen from free-text titles and descriptions
     - `get_product_details_*`: pagination and page parsing
     - `main()`: writes one CSV per category to `Main/Products/<Site>/<Category>.csv`
   - The three scrapers are near-duplicates, so a parsing fix usually needs applying to all three.
2. **`DB.py`** (`main(db_path=DB_PATH)`): deletes and recreates the DB, creates the `<site>_<category>` tables (raw DDL strings at the top) and loads the CSVs, normalising prices, resolution and so on.
   - Values are inlined into SQL through `sql_value()`, not bound parameters.
   - Only `Pc Portable Gamer`, `Pc de Bureau Gamer` and `Ecran Gamer` are loaded. The other scraped categories (Casque, Clavier, Souris, Tapis Souris) have CSVs but no tables.
3. **`ProductMatching.py`** (`main(db_path=DB_PATH)`): for each Tunisianet product, finds the best-scoring Mytek and Scoop Gaming counterparts.
   - Scoring is thefuzz title matching plus per-category spec comparison (`specs_similarity_*`). A score above 60 counts as a match.
   - Results go to the `matched_<category>` tables, which hold the three links and have foreign keys to the site tables.
   - **Tunisianet is the anchor.** Every Tunisianet product gets a matched row, and products sold only by Mytek or Scoop never appear.
4. **`build_db.py`**: `DB.main` followed by `ProductMatching.main`. This is the entry point for rebuilding.
5. **Web app** (`app.py`): Flask + Flask-SQLAlchemy.
   - The DB path is `TUNICOMPARE_DB` (env) or `<repo>/tunicompare.db`. It is opened through a custom `creator` as a SQLite URI with `mode=ro&immutable=1`; `Path.as_uri()` handles spaces in the path.
   - Tables are reflected lazily with `automap_base` in `get_models()`. An unreadable DB therefore makes `/load_products` return 503 JSON rather than breaking boot.
   - Pages (`/`, `/shop/laptop|desktop|screen`) are Jinja templates extending `templates/base.html`. The product grids are filled client-side from `GET /load_products?product_type=<pc_portable_gamer|pc_bureau_gamer|ecran_gamer>&limit=&offset=`, which orders by Tunisianet price and returns `{tunisianet, mytek, scoopgaming}` per product (the last two may be `null`).
   - `public/static/JS/product-list.js` does the infinite scroll (IntersectionObserver sentinel) and the best-price highlighting.

**Naming.** The DB identifiers must be lowercase, because `app.py` uses `Base.classes.matched_pc_portable_gamer`, `product.linktunisianet` and so on (Postgres used to fold names to lowercase). The DDL strings are written in CamelCase, and `Create_Table` lowercases them on execution. Keep FK `REFERENCES` targets inside those strings so they get lowercased too. The API/table slugs (`pc_portable_gamer`, `pc_bureau_gamer`, `ecran_gamer`) differ from the scraper category/CSV names (`Pc Portable Gamer`, `Pc de Bureau Gamer`, `Ecran Gamer`).

**Static files** live in `public/static/`. Vercel serves `public/**` from its CDN and doesn't use Flask's static folder. `app.py` sets `static_folder="public/static", static_url_path="/static"`, so `url_for('static', ...)` produces the same `/static/...` URLs locally and on Vercel.

`.vercelignore` keeps `Main/`, `Screenshots/`, `docs/`, `tests/` and `.venv/` out of the deployment. Design and plan docs are in `docs/superpowers/`.

## Known issues (deferred)

- **Desktop matching is many-to-one.** 54 Tunisianet desktops match Scoop Gaming's only 2 desktops, and 332 match just 156 Mytek desktops, so many "best price" highlights on the desktop page compare different machines. Likely fix: let each store's product match at most one Tunisianet product, and/or use a stricter threshold.
- About 11% of the 2025 product image URLs, and many product links, now return 404 or 403 from the retailers.
- The scrapers are unrepaired since summer 2025. Their `main()` functions still write CSVs with Windows-style paths (`f"Main\Products\Tunisianet\{item}.csv"`), which on Linux produce backslash-named files instead of writing into `Main/Products/`. The planned follow-up is to repair them and run them on a schedule with GitHub Actions.
- `app.py:best_price` is unused and crashes on `None` entries. The best-price logic lives in the JS.
- The README's project-structure tree doesn't match the real files. Trust the code.
