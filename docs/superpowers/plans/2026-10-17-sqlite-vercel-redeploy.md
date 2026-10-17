# SQLite Rebuild + Vercel Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild TuniCompare's database as a committed SQLite file from the 2025 CSVs and serve the Flask app live on Vercel's free plan.

**Architecture:**
- `Scripts/DB.py` and `Scripts/ProductMatching.py` move from psycopg2 to the stdlib `sqlite3`.
- A new `Scripts/build_db.py` rebuilds `tunicompare.db` from scratch, and the file is committed.
- `app.py` opens it read-only.
- Static assets move to `public/static/` so Vercel's CDN serves them at the same `/static/...` URLs.
- Work happens on branch `sqlite-vercel`. A Vercel preview checks it, then it is merged to `main` and pushed for production.

**Tech Stack:** Python 3.12, Flask 3.1, Flask-SQLAlchemy 3.1, SQLAlchemy 2.0 automap, sqlite3, thefuzz, pytest, Vercel (Hobby) via Vercel MCP.

**Spec:** `docs/superpowers/specs/2026-10-17-sqlite-vercel-redeploy-design.md`

## Global Constraints

- **Free only.** Vercel Hobby, no paid service.
- **The 2025 CSVs under `Main/Products/` are never edited.** Only their line endings are normalised back to the committed LF.
- **Python ≥ 3.12.** f-strings reuse the same quote type. Pin `3.12` for Vercel.
- **Lowercase identifiers.** Table and column names in the built DB must be lowercase, matching `app.py`:
  - tables: `matched_pc_portable_gamer`, `tunisianet_pc_bureau_gamer`, …
  - columns: `linktunisianet`, `linkmytek`, `linkscoopgaming`
- **Read-only at runtime.** The app opens the DB read-only and never writes.
- **No UI or feature changes. No date label.**
- **Minimal edits** that keep the owner's structure, naming and style. Don't fix unrelated bugs; the desktop many-to-one matching is deferred.
- **Branch and deploy flow.** Work on `sqlite-vercel`. Push to `main` only after the preview passes every check.
- **Vercel scope:** user `tammam-bt`, team id `team_cgvRVzofSKE1Eeg56mqmGfYv`, repo `tammam-bt/TuniCompare`.
- **Commit messages** end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Expected data

Row counts are CSV lines minus the header. The CSVs contain no embedded newlines or duplicate links.

| table | rows |
|---|---|
| tunisianet_pc_portable_gamer / _pc_bureau_gamer / _ecran_gamer | 250 / 525 / 32 |
| mytek_… | 221 / 156 / 25 |
| scoopgaming_… | 41 / 2 / 26 |
| matched_… (one row per Tunisianet product) | 250 / 525 / 32 |

## Review Focus

1. **Repo path with spaces.** The owner's checkout is `~/VS Code Projects/TuniCompare`. Build and app must both work when the DB path contains a space. Test: the shared `built_db` fixture builds into a directory named `db dir`.
2. **DB file missing.** `/load_products` should return the JSON 503 `{"error": "Database unavailable"}` and the app should still boot. Test: `test_missing_db_returns_503`.
3. **Read-only filesystem, as on Vercel.** Serving must work when the DB file and its directory are not writable. Test: `test_read_only_db_serves`.
4. **Scrolling past the end.** `offset` beyond the last product returns `[]`, so infinite scroll stops cleanly. Test: `test_offset_past_end_is_empty`.
5. **Rebuilding over an existing DB.** The result matches a fresh build, with no duplicated or stale rows. Test: `test_rebuild_is_idempotent`.

---

### Task 1: Repo hygiene and branch

**Files:**
- Create: `.gitattributes`
- Modify: the working-tree line endings of the 39 CRLF-only files. `app.py` keeps its real changes, converted to LF.

- [ ] **Step 1: Restore LF in CRLF-only files.**
  - `git diff --ignore-cr-at-eol --name-only` lists the files with real changes. It should list only `app.py`.
  - Run `git checkout -- <every other modified file>`.
  - Run `sed -i 's/\r$//' app.py`.
- [ ] **Step 2: Add `.gitattributes`** with `* text=auto eol=lf`.
- [ ] **Step 3: Fast-forward `main`.** Run `git pull --ff-only origin main`. Expected: fast-forward to `e2411a4` (README only).
- [ ] **Step 4: Tag the snapshot.** Run `git tag -a data-2025-08 -m "Last Postgres/Render version and summer-2025 CSV snapshot" e2411a4`.
- [ ] **Step 5: Create the branch.** Run `git switch -c sqlite-vercel`. The uncommitted `app.py` change and `CLAUDE.md` move with it.
- [ ] **Step 6: Recreate the venv** with `python3 -m venv --clear .venv`. The old one is a Windows venv. Requirements are installed in Task 2.
- [ ] **Step 7: Verify.** `git status --short` shows only these:
  - `M app.py`
  - `?? .gitattributes`
  - `?? CLAUDE.md`
  - `?? docs/`
  - the 3 untracked PNGs in `static/Resources/`, which are left untracked
- [ ] **Step 8: Commit.** Run `git add .gitattributes docs && git commit` with the message `docs: add SQLite/Vercel design and plan; enforce LF line endings`.

### Task 2: SQLite build pipeline

**Files:**
- Modify: `Scripts/DB.py`
- Modify: `Scripts/ProductMatching.py`
- Modify: `Run.py`
- Modify: `requirements.txt`
- Create: `Scripts/build_db.py`
- Create: `requirements-dev.txt`
- Create: `pytest.ini`
- Create: `tests/conftest.py`
- Create: `tests/test_build_db.py`
- Create: `.gitignore` entry for `.pytest_cache/` (already present, no change needed)

**Interfaces:**
- Produces:
  - `Scripts.DB.DB_PATH: str`, the absolute path `<repo>/tunicompare.db`.
  - `Scripts.DB.main(db_path: str = DB_PATH) -> None`. Deletes `db_path` if it exists, creates the 9 site tables and loads the CSVs.
  - `Scripts.ProductMatching.main(db_path: str = DB_PATH) -> None`. Creates and fills the 3 `matched_*` tables in an existing DB.
  - `Scripts.build_db.main(db_path: str = DB_PATH) -> None`. Calls the two in order.
  - The command `python -m Scripts.build_db`.
  - The pytest fixture `built_db -> str`, session-scoped: the path of a DB built into `tmp/db dir/tunicompare.db`.

- [ ] **Step 1: Split requirements.**
  - `requirements.txt` is web only (Vercel): `Flask==3.1.1`, `Flask-SQLAlchemy==3.1.1`, `SQLAlchemy==2.0.42`, `Werkzeug==3.1.3`, `Jinja2==3.1.6`, `MarkupSafe==3.0.2`, `itsdangerous==2.2.0`, `click==8.2.1`, `blinker==1.9.0`, `greenlet==3.2.3`, `typing_extensions==4.14.1`.
  - `requirements-dev.txt` holds `-r requirements.txt` plus the scraper and build deps from the old file (`beautifulsoup4`, `bs4`, `soupsieve`, `requests`, `certifi`, `charset-normalizer`, `idna`, `urllib3`, `thefuzz`, `RapidFuzz`, `packaging`) and `pytest==8.4.1`.
  - Drop `psycopg2`, `gunicorn`, `dotenv`, `python-dotenv` and `colorama`.
  - Install with `.venv/bin/pip install -r requirements-dev.txt`.
- [ ] **Step 2: Add `pytest.ini`** containing `[pytest]`, `pythonpath = .` and `testpaths = tests`.
- [ ] **Step 3: Write the failing tests in `tests/test_build_db.py`.** Add the `built_db` fixture to `tests/conftest.py`: `tmp_path_factory.mktemp("db dir") / "tunicompare.db"`, then `build_db.main(str(path))`.
  - `test_tables_are_lowercase`: the set of `name` in `sqlite_master WHERE type='table'` equals the 12 lowercase names, `{site}_{type}` for site in tunisianet/mytek/scoopgaming and type in pc_portable_gamer/pc_bureau_gamer/ecran_gamer, plus `matched_{type}`.
  - `test_row_counts`: each table's `COUNT(*)` equals the Expected data table above.
  - `test_matched_columns_lowercase`: `PRAGMA table_info(matched_pc_portable_gamer)` names are `["linktunisianet", "linkmytek", "linkscoopgaming"]`.
  - `test_matched_foreign_keys_lowercase`: every `PRAGMA foreign_key_list(matched_X)` row's `table` is lowercase and in the set of table names.
  - `test_rebuild_is_idempotent`: copy `built_db` to a new tmp path, run `build_db.main` on that path again, and get the same row counts as `test_row_counts`.
- [ ] **Step 4: Run** `.venv/bin/pytest tests/test_build_db.py -q`. Expected: FAIL (`Scripts.build_db` does not exist).
- [ ] **Step 5: Port `Scripts/DB.py`.**
  - `import sqlite3` replaces `psycopg2`. Drop `dotenv`.
  - Define `REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` and `DB_PATH = os.path.join(REPO_ROOT, "tunicompare.db")`.
  - CSV path: `os.path.join(REPO_ROOT, "Main", "Products", website, f"{item}.csv")`.
  - `Create_Table` executes `query[1].lower()`, with a comment that Postgres folded names to lowercase and `app.py` relies on that.
  - `main(db_path=DB_PATH)` does the following. The rest of `Populate_tables` is unchanged.
    1. Remove an existing file.
    2. Connect with `sqlite3.connect(db_path)`.
    3. Run `Create_Table` for each entry in `Table_Queries`. This replaces the `INFORMATION_SCHEMA` check.
    4. Run `Populate_tables`.
    5. Commit and close.
- [ ] **Step 6: Port `Scripts/ProductMatching.py`.**
  - `sqlite3` replaces psycopg2. Drop `dotenv`.
  - `from Scripts.DB import DB_PATH`.
  - `Create_Table` executes `query[1].lower()`.
  - `main(db_path=DB_PATH)` connects with `sqlite3.connect(db_path)`, creates the matched tables (no `INFORMATION_SCHEMA` check), runs the existing matching loop unchanged, commits, and closes the connection once.
- [ ] **Step 7: Create `Scripts/build_db.py`.** `main(db_path=DB_PATH)` calls `DB.main(db_path)` and then `ProductMatching.main(db_path)`, with an `if __name__ == "__main__": main()` guard.
- [ ] **Step 8: Update `Run.py`.** It runs the three scrapers, then `build_db.main()`. Remove the stale `runpy.run_path("Main/Code/App/app.py")` line.
- [ ] **Step 9: Run** `.venv/bin/pytest tests/test_build_db.py -q`. Expected: all pass.
- [ ] **Step 10: Commit** with the message `feat: build the database as SQLite from the committed CSVs`.

### Task 3: App on SQLite, static assets for Vercel, committed DB

**Files:**
- Modify: `app.py`
- Move: `static/` → `public/static/` (`git mv`; untracked PNGs move with it and stay untracked)
- Create: `tunicompare.db`, generated by `python -m Scripts.build_db`
- Create: `tests/test_app.py`

**Interfaces:**
- Consumes: the `built_db` fixture and `Scripts.build_db.main` from Task 2.
- Produces: `app.DB_PATH: str`, taken from env `TUNICOMPARE_DB` or defaulting to `<dir of app.py>/tunicompare.db`. Also the Flask `app`, with `static_folder="public/static"` and `static_url_path="/static"`.

- [ ] **Step 1: Write the failing tests in `tests/test_app.py`.**
  - Helper `make_client(db_path) -> FlaskClient`. Set `os.environ["TUNICOMPARE_DB"] = db_path`, `importlib.reload` the `app` module (import it first if needed), and return `app.app.test_client()`. Restore the env in the fixture teardown.
  - `test_pages_render`: `/`, `/shop/laptop`, `/shop/desktop` and `/shop/screen` each return 200.
  - `test_static_served`: `/static/CSS/shop.css`, `/static/JS/product-list.js` and `/static/Resources/Logo.png` each return 200.
  - `test_load_products_counts`: for `(pc_portable_gamer, 250)`, `(pc_bureau_gamer, 525)` and `(ecran_gamer, 32)`, `GET /load_products?product_type=T&limit=1000&offset=0` returns a list of exactly N items.
    - Each item's keys are `{"tunisianet", "mytek", "scoopgaming"}`.
    - `item["tunisianet"]` has keys `{"link", "title", "image", "price"}`.
    - Tunisianet prices are non-decreasing.
  - `test_default_paging`: `/load_products?product_type=pc_portable_gamer` returns 5 items, the same as the first 5 of the limit-1000 call.
  - `test_offset_past_end_is_empty`: `offset=10000` returns `[]` with status 200.
  - `test_missing_db_returns_503`: point at `tmp_path / "nope.db"`. `/` returns 200, and `/load_products` returns 503 with JSON `{"error": "Database unavailable"}`.
  - `test_read_only_db_serves`:
    1. Copy `built_db` into a fresh tmp dir.
    2. `chmod` the file to `0o444` and the dir to `0o555`.
    3. `/load_products?product_type=ecran_gamer&limit=1000` returns 32 items.
    4. Restore permissions in a `finally`, and check that no `-journal`/`-wal` file was created.
- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_app.py -q`. Expected: FAIL (the app still reads `dburl`, and the static folder has moved or isn't set).
- [ ] **Step 3: Run `git mv static public/static`.**
- [ ] **Step 4: Update `app.py`.**
  - Drop `dotenv`, `dburl` and the `postgres://` rewrite.
  - `DB_PATH = os.getenv("TUNICOMPARE_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tunicompare.db"))`.
  - `Flask(__name__, static_folder="public/static", static_url_path="/static")`.
  - Set `SQLALCHEMY_DATABASE_URI = "sqlite://"` and `SQLALCHEMY_ENGINE_OPTIONS = {"creator": ...}`. The creator returns `sqlite3.connect(Path(DB_PATH).as_uri() + "?mode=ro&immutable=1", uri=True, check_same_thread=False)`. `as_uri()` percent-encodes spaces in the path.
  - Short comments: Vercel's filesystem is read-only, and Vercel serves `public/**` from its CDN.
  - The rest of `app.py`, including the lazy `get_models` and the 503 handling, is unchanged.
- [ ] **Step 5: Run** `.venv/bin/pytest -q`. Expected: all tests in both files pass.
- [ ] **Step 6: Build the real DB** with `.venv/bin/python -m Scripts.build_db`.
  - Smoke-check with `.venv/bin/python app.py` in the background.
  - `curl -s 'localhost:5000/load_products?product_type=pc_bureau_gamer&limit=1000' | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))'` should print `525`.
  - Stop the server.
- [ ] **Step 7: Commit.** Run `git add -A app.py public static tests tunicompare.db`; the untracked PNGs are not added, so check `git status`. Message: `feat: serve the committed SQLite database read-only; move static assets under public/ for Vercel`.

### Task 4: Vercel config, preview deployment

**Files:**
- Create: `.python-version` (`3.12`)
- Create: `.vercelignore` (`Main/`, `Screenshots/`, `docs/`, `tests/`, `.venv/`)
- Delete: `Procfile`

- [ ] **Step 1: Create the files above, delete `Procfile`, and commit.** Message: `chore: Vercel config (Python 3.12, ignore non-runtime files); drop Render Procfile`.
- [ ] **Step 2: Push** with `git push -u origin sqlite-vercel` and `git push origin data-2025-08`. Do not push `main`.
- [ ] **Step 3: Create the project.** Call `create_git_project(repo="tammam-bt/TuniCompare", teamId="team_cgvRVzofSKE1Eeg56mqmGfYv", projectName="tunicompare", deploy=false)`. If it returns `requires_user_action`, the Vercel GitHub app lacks repo access: report the dashboard URL and stop.
- [ ] **Step 4: Trigger and wait for the branch preview.**
  - Trigger a deployment of `sqlite-vercel` with `create_deployment` from the git ref, or push an empty commit to the branch.
  - Poll `get_deployment` until `READY`.
  - On `ERROR`, read the build logs, fix, and push again.
- [ ] **Step 5: Verify the preview.** Use `web_fetch_vercel_url`, since previews are protected.
  - `/`, `/shop/laptop`, `/shop/desktop` and `/shop/screen` return 200.
  - `/static/CSS/shop.css` returns 200.
  - `/load_products?product_type=X&limit=1000` returns 250/525/32 items.
  - `get_runtime_errors` shows no errors.

### Task 5: Docs, merge to main, production check

**Files:**
- Modify: `README.md`, only the live-demo links/URL and the stack rows: PostgreSQL→SQLite, Render→Vercel.
- Modify: `CLAUDE.md`, to the new architecture, commands and known issues, including the deferred desktop many-to-one matching.

- [ ] **Step 1: Get the production domain** with `get_project` / `list_project_domains`, e.g. `tunicompare.vercel.app`.
- [ ] **Step 2: Update `README.md`.** Replace `https://tunicompare.onrender.com/` everywhere with the production URL. Update the PostgreSQL/Render badges and table rows and the "Run Locally" steps:
  1. create the venv
  2. `pip install -r requirements-dev.txt`
  3. `python -m Scripts.build_db`
  4. `python app.py`

  Remove the Postgres/Docker/.env setup.
- [ ] **Step 3: Rewrite `CLAUDE.md`** to match. Commit with the message `docs: README and CLAUDE.md for the SQLite/Vercel setup`.
- [ ] **Step 4: Merge and push** with `git switch main && git merge --ff-only sqlite-vercel && git push origin main`. This is the production deploy.
- [ ] **Step 5: Check production.**
  - Wait for the production deployment to be `READY`.
  - Repeat the Task 4 Step 5 checks against the public production URL.
  - Check in Chrome that the home featured list renders, each shop page shows price columns with best-price highlighting, scrolling loads more cards, and the console has no errors from our own origin. Failed third-party image loads are acceptable.
  - `get_runtime_errors` shows none.
