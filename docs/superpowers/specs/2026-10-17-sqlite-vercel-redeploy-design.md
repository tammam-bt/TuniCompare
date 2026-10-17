# TuniCompare: SQLite rebuild and Vercel deployment

Date: 2026-10-17
Status: approved 2026-10-17

## Intent

TuniCompare was a summer-2025 learning project. It was live on Render with a
Postgres database, and that database is gone. The owner wants it running live
again as a showcase, on free hosting only, without losing the data collected
last summer.

This is **project 1 of 2**:

1. **This document.** Rebuild the database from the CSVs committed in 2025, and
   put the site live on Vercel with that data.
2. **Later, separate design.** Repair the three scrapers and run them on a
   schedule with GitHub Actions, so prices refresh by themselves.

Project 1 must not depend on the scrapers working.

## Goals

- The site is live on a free Vercel URL and works end to end:
  - home page with its featured list
  - laptop, desktop and screen shop pages
  - infinite scroll
  - three-store price comparison with the best price highlighted
- The data is last summer's snapshot, rebuilt from `Main/Products/*/*.csv`.
- One local command rebuilds the database from the CSVs, with no database server
  to install.
- Nothing in the hosting can be paused, expired or deleted for inactivity.
- The repo is runnable on Linux.

## Non-goals

- Fixing or running the scrapers (project 2).
- Scheduled refreshes, or keeping archive data and fresh data side by side
  (project 2).
- UI or feature changes, or a redesign.
- A "prices as of" date label. The owner explicitly does not want one.
- Fixing the other bugs found in the codebase, unless they block this goal.
  Example: `best_price` in `app.py` is unused.

## Anti-goals

- **Any paid service.** Hosting must be free, with no exceptions.
- **Losing or altering the 2025 data.** The committed CSVs are the source of
  truth and are not edited.
- **Hosting that can disappear while idle.** Supabase deleted the last database
  for inactivity, and Render's free Postgres expires after 30 days.
- **Rewriting working code.** This was the owner's learning project, so changes
  stay small and keep their structure, naming and style.

## Decisions

### Made by the owner

- **SQLite replaces Postgres.** The owner's view is that Postgres isn't needed
  architecturally. There are about 1,300 product rows across the 9 tables used,
  the site only reads, and writes come only from the offline build.
- **Vercel hosts the site, free Hobby plan.** No other platform is used for
  project 1.
- **Fresh Vercel project.** The old deployment was on Render, not Vercel, so
  this is a new Vercel project created from the existing GitHub repo
  (`tammam-bt/TuniCompare`).
- **Keep Flask.** The site is not converted to static pages.
- **No date label on the site.**
- **Work on a side branch, then push to `main`.** `main` stays intact while
  the work happens on a side branch. Once everything has been checked, the
  branch is merged and pushed to `main`, which is the production branch.
- **Claude manages Vercel through the Vercel MCP server.** Claude creates and
  manages the project. The owner only signs in. The server was installed on
  2026-10-17 (`claude mcp add --transport http --scope user vercel
  https://mcp.vercel.com`).
- **The desktop matching bug is left for later.** See "Later" below.

### Made by Claude (owner may override)

- **The built `.db` file is committed to the repo** and deployed with the app,
  opened read-only. Building it on Vercel at deploy time was rejected: Vercel
  would then need the matching dependencies, and the build would be harder to
  check.
- **Rebuild from scratch every time.** Each build deletes the old `.db` and
  creates it fresh from the CSVs. This avoids depending on the existing
  upsert/delete logic, and on SQLite's foreign-key cascades, which are off by
  default.
- **Tag the snapshot.** A git tag (e.g. `data-2025-08`) marks the commit holding
  last summer's CSVs, so the archive is easy to find even after project 2
  starts committing fresh data.
- **Fix the line endings.** 39 of the 40 uncommitted files differ from the
  commit only by CRLF line endings, left over from the Windows checkout. Their
  content, including all CSV data, is identical. These go back to LF, with a
  `.gitattributes` to keep them that way. The one real uncommitted change, a
  refactor of `app.py` (lazy model loading, a 503 when the DB is unreachable),
  is kept.
- **Update the docs.** The README's live-demo link and stack are updated to
  Vercel and SQLite, and `CLAUDE.md` to the new architecture. The README's
  inaccurate file tree is left alone (out of scope).

## What needs to change (known so far)

### `Scripts/DB.py` and `Scripts/ProductMatching.py`

- **Driver.** Switch from `psycopg2` to the standard-library `sqlite3`.
  Queries are built as SQL strings with values escaped by `sql_value`, not
  through `%s` placeholders, so the query text mostly carries over.
  `ON CONFLICT ... DO UPDATE` and `TRUE`/`FALSE` both work in SQLite.
- **Table lookup.** Replace the `INFORMATION_SCHEMA.TABLES` existence checks.
  With rebuild-from-scratch, `CREATE TABLE` on a new file is enough.
- **Identifier case.** Postgres lowercases unquoted names, so tables are
  `matched_pc_portable_gamer` and columns `linktunisianet`. `app.py` relies on
  these lowercase names. SQLite keeps names as written (`Matched_Pc_Portable_Gamer`,
  `linkTunisianet`), which would break `Base.classes.matched_...` and
  `product.linktunisianet`. The tables in the built file must reflect with the
  same lowercase names `app.py` uses.
- **Relationships.** Keep the `FOREIGN KEY` declarations in the `matched_*`
  tables. `app.py`'s `.join(Tunisianet)` depends on automap finding them.
- **File paths.** `Populate_tables` opens CSVs with Windows paths
  (`f"Main\Products\{website}\{item}.csv"`), which fail on Linux. Use
  forward-slash or `os.path` paths relative to the repo root.

### Build entry point

- Add a way to build the `.db` from the CSVs alone: `DB.main()` followed by
  `ProductMatching.main()`, without running the scrapers.
- `Run.py` currently scrapes first, then launches a stale path
  (`Main/Code/App/app.py`). How `Run.py` relates to the new entry point is left
  to the builder.

### `app.py`

- Point SQLAlchemy at the committed SQLite file:
  - Use a path resolved relative to `app.py`, not the current working
    directory.
  - Open it read-only, since Vercel's filesystem is read-only.
  - Drop the `dburl` and `postgres://` handling.

### Dependencies

- Remove `psycopg2` from what Vercel installs. It needs a compiler and libpq
  and would likely break the build.
- Whether to split the web dependencies from the build and scraper ones
  (`thefuzz`, `RapidFuzz`, `bs4`, `requests`) is left to the builder.
- **Python 3.12 or newer is required.** `DB.py` and `ProductMatching.py` reuse
  the same quote type inside f-strings (`f"'{val.replace("'", "''")}'"`), which
  only parses on 3.12+. Local Python is 3.12.3.
- **Recreate the local `.venv`.** It is a Windows venv (`Scripts/`, `Lib/`) and
  doesn't run on Linux.

### Vercel

- New project, imported from the GitHub repo, on the free Hobby plan.
- **Order of work:**
  1. Push the side branch.
  2. Check its Vercel preview deployment.
  3. Merge into `main` and push. That push is the production deploy.
- **Tooling.** Use the Vercel MCP server. It was connected on 2026-10-17 as
  user `tammam-bt`, Hobby plan, personal scope `team_cgvRVzofSKE1Eeg56mqmGfYv`,
  with no other teams.
  - `create_git_project` links the GitHub repo and auto-deploys on push.
  - By default it creates a preview deployment from `main` straight away. Pass
    `deploy: false`, or create the project only after the side branch is
    pushed, so the unported Postgres `main` isn't deployed.
  - Use `get_deployment`, the build logs and `get_runtime_errors` to check
    deployments.
- The builder confirms how Vercel currently detects and serves a Flask app,
  and adds config (`vercel.json`, `.vercelignore`, a Python version pin) only if
  needed. The repo has no Vercel config today. Points to confirm:
  - Flask's `static/` folder is actually served, which the CSS, JS and images
    depend on.
  - The `.db` file is included in the deployed function.
- `Procfile` (Render-specific) can go.

## Data facts

- The site uses these CSVs: `Pc Portable Gamer`, `Pc de Bureau Gamer` and
  `Ecran Gamer`, for each of `Tunisianet`, `Mytek` and `Scoop Gaming`.
  - Row counts including headers: Tunisianet 251/526/33, Mytek 222/157/26,
    Scoop Gaming 42/3/27.
  - Scoop Gaming has only 2 desktops, so that column will be mostly empty on the
    desktop page. That reflects the data, not a bug.
- The other categories (Casque, Clavier, Souris, Tapis Souris) have CSVs but no
  tables. They stay unused.
- Matching anchors on Tunisianet. Only products sold by Tunisianet appear.
  This is existing behaviour and is kept.
- **Images have decayed** (reviewer's check, 2026-10-17). Product images
  load straight from the retailers. Of 807 Tunisianet image URLs, 90 (11%) now
  return 404 or 403, and the browser logs each failed request. *Claude's call:*
  these third-party failures are accepted and don't count against "Done
  means". Fixing them would mean altering the 2025 data or changing the UI.
  Product links have decayed in the same way.
- **Dry run already done** (reviewer, in a throwaway copy). The existing load
  and matching scripts, ported to SQLite with lowercase DDL, loaded every row
  and filled all three `matched_*` tables. `app.py`, opening the file
  read-only, served 250/525/32 products through `/load_products`, and the
  automap join worked. No hidden blockers were found.
- **GitHub is one commit ahead of the local copy** (`e2411a4`, a README-only
  change from 2025-08-04). Pull it before starting. Restore LF endings first,
  so the README's CRLF changes don't conflict with it.

## Done means

1. On a clean Linux checkout, these steps produce the `.db`, and `python app.py`
   serves a working site locally:
   - create a venv
   - install the requirements
   - run the build command
2. The deployed Vercel URL shows all of the following, with no errors in the
   browser console from our own code or requests, and none in the Vercel logs:
   - home page featured list
   - all three shop pages
   - infinite scroll
   - three-store price columns with best-price highlighting
3. The 2025 CSVs are unchanged, apart from line endings, and the snapshot is
   tagged.
4. README and `CLAUDE.md` describe the new setup. `CLAUDE.md` lists the
   deferred matching bug.
5. The side branch is merged and pushed to `main`, and production is serving
   from `main`.

## Later (not this project)

- **Desktop matching produces many-to-one matches.** Found by the reviewer.
  - 54 Tunisianet desktops match Scoop Gaming's only 2 desktops, and 332 match
    just 156 Mytek desktops. Many "best price" highlights on the desktop page
    therefore compare different machines.
  - Likely fix: each store's product matches at most one Tunisianet product,
    and/or a stricter threshold in `ProductMatching.py`.
  - The owner chose to defer it. It is recorded in `CLAUDE.md` as a known
    issue.
- **Decayed images and links:** about 11% of image URLs return 404 or 403.
  Fresh scraping in project 2 fixes this.
- **Scraper repair and scheduled refresh:** project 2.

## Left to the builder

- Exact build command and module layout.
- Whether to lowercase identifiers in the DDL or handle the names some other
  way, as long as `app.py` sees lowercase names.
- Whether `requirements.txt` is split.
- The exact Vercel configuration.
- Commit order.
