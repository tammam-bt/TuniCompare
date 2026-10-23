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
3. **`ProductMatching.py`** (`main(db_path=DB_PATH)`): pairs each Tunisianet product with at most one Mytek and one Scoop Gaming listing.
   - `similarity_score` returns 999 when both listings carry the same manufacturer reference (`site_id`).
   - Otherwise, `spec_conflict` first rejects (score 0) any pair whose known specs disagree. The specs come from the columns and from the titles:
     - model code, brand, GPU (including Ti/Super/XT), RAM and exact CPU;
     - screens: panel type;
     - desktops: GPU memory and monitor bundles. A desktop pair is also rejected unless both sides name the exact CPU.
   - Pairs that pass are scored as the average of the thefuzz title score and the per-category spec score (`specs_similarity_*`). A score of at least `MATCH_THRESHOLD` (75) counts.
   - `assign_one_to_one` then takes pairs greedily by score, so a store listing is used for at most one Tunisianet product.
   - Results go to the `matched_<category>` tables, which hold the three links and have foreign keys to the site tables.
   - `python -m Scripts.eval_matching` prints precision and match counts against the hand labels in `docs/matching-labels.csv`. Label any new pairs after changing the matching (`--unlabelled` lists them).
   - **Tunisianet is the anchor.** Every Tunisianet product gets a matched row, and products sold only by Mytek or Scoop never appear.
4. **`build_db.py`**: `DB.main` followed by `ProductMatching.main`. This is the entry point for rebuilding.
5. **Web app** (`app.py`): Flask + Flask-SQLAlchemy.
   - The DB path is `TUNICOMPARE_DB` (env) or `<repo>/tunicompare.db`, made absolute. It is opened through a custom `creator` as a SQLite URI with `mode=ro&immutable=1`; `Path.as_uri()` handles spaces in the path.
   - `SQLALCHEMY_DATABASE_URI` is still the file URL `sqlite:///<path>`, because that makes SQLAlchemy use a per-thread pool. Don't change it to `sqlite://`: Flask-SQLAlchemy would then force a single shared connection (`StaticPool`), and concurrent requests return 500s or each other's results. `test_concurrent_*` covers this.
   - Tables are reflected lazily with `automap_base` in `get_models()`. An unreadable DB therefore makes `/load_products` return 503 JSON rather than breaking boot.
   - Pages (`/`, `/shop/laptop|desktop|screen`) are Jinja templates extending `templates/base.html`. The product grids are filled client-side from `GET /load_products?product_type=<pc_portable_gamer|pc_bureau_gamer|ecran_gamer>&limit=&offset=`, which orders by Tunisianet price and returns `{tunisianet, mytek, scoopgaming}` per product (the last two may be `null`).
   - `public/static/JS/product-list.js` does the infinite scroll (IntersectionObserver sentinel) and the best-price highlighting.

**Naming.** The DB identifiers must be lowercase, because `app.py` uses `Base.classes.matched_pc_portable_gamer`, `product.linktunisianet` and so on (Postgres used to fold names to lowercase). The DDL strings are written in CamelCase, and `Create_Table` lowercases them on execution. Keep FK `REFERENCES` targets inside those strings so they get lowercased too. The API/table slugs (`pc_portable_gamer`, `pc_bureau_gamer`, `ecran_gamer`) differ from the scraper category/CSV names (`Pc Portable Gamer`, `Pc de Bureau Gamer`, `Ecran Gamer`).

**Static files** live in `public/static/`. Vercel serves `public/**` from its CDN and doesn't use Flask's static folder. `app.py` sets `static_folder="public/static", static_url_path="/static"`, so `url_for('static', ...)` produces the same `/static/...` URLs locally and on Vercel.

`.vercelignore` keeps `Main/`, `Screenshots/`, `docs/`, `tests/` and `.venv/` out of the deployment. Design and plan docs are in `docs/superpowers/`.

## Known issues (deferred)

- **Matching favours precision over coverage.** It has been one-to-one since October 2026. Against the hand labels, every pair in the DB is labelled:
  - laptops: 145 of 148 pairs are the same product;
  - desktops: 27 of 27;
  - screens: 14 of 14.

  Many real matches are still missing:
  - Tunisianet often lists one SKU several times (bundles, Windows 11 Pro), and only one of those listings gets the store's price.
  - Mytek desktop titles name only the CPU generation, so those desktops match only when the CPU column has the exact model.
  - Some true pairs score just under 75 (Redragon Pearl vs Pearl II).
  - No Scoop Gaming desktop matches.

  The remaining wrong laptop pairs are the Lenovo LOQ 15IAX9E vs 15IAX9 (one model code extends the other) and an ASUS Flow Z13 whose two titles disagree on the CPU despite a shared reference.
- About 11% of the 2025 product image URLs, and many product links, now return 404 or 403 from the retailers.
- The scrapers are unrepaired since summer 2025. Their `main()` functions still write CSVs with Windows-style paths (`f"Main\Products\Tunisianet\{item}.csv"`), which on Linux produce backslash-named files instead of writing into `Main/Products/`. The planned follow-up is to repair them and run them on a schedule with GitHub Actions.
- `app.py:best_price` is unused and crashes on `None` entries. The best-price logic lives in the JS.
- The README's project-structure tree doesn't match the real files. Trust the code.
