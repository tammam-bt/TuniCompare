import sqlite3
import subprocess

import pytest

from Scripts import ProductMatching
from Scripts.DB import DB_PATH, REPO_ROOT

TYPES = ["pc_portable_gamer", "pc_bureau_gamer", "ecran_gamer"]
SITES = ["tunisianet", "mytek", "scoopgaming"]
STORE_COLUMNS = {"mytek": "linkmytek", "scoopgaming": "linkscoopgaming"}


def laptop(**overrides):
    product = {
        "title": "Pc Portable Gamer MSI Thin 15 B13U / i5-13420H / RTX 2050 4G / 8 Go / 512 Go SSD",
        "link": "https://example.test/a", "site_id": "[A]", "brand": "msi", "model": None,
        "cpu_brand": "Intel", "cpu_model": "i5-13420h", "cpu_cores": 8, "ram_size": 8,
        "gpu_brand": "nvidia", "gpu_model": "rtx-2050", "gpu_memory": 4,
        "storage_type": "ssd", "storage_size": 512, "screen_type": "ips", "screen_size": 15.6,
        "screen_resolution": "fhd", "screen_refresh_rate": 144,
    }
    product.update(overrides)
    return product


def test_normalize_gpu():
    assert ProductMatching.normalize_gpu("RTX-3050") == "rtx3050"
    assert ProductMatching.normalize_gpu("rtx 3050") == "rtx3050"
    assert ProductMatching.normalize_gpu("rtx3050") == "rtx3050"


def test_model_codes():
    assert ProductMatching.model_codes("Lenovo LOQ 15IAX9 i5-12450HX 24Go RTX 3050") == {"15iax9"}


def test_conflicting_gpu_rejected():
    rtx2050 = laptop()
    rtx3050 = laptop(title=rtx2050["title"].replace("RTX 2050", "RTX 3050"), link="https://example.test/b",
                     site_id="[B]", gpu_model="rtx 3050")
    # Without the GPU difference the pair is a match, so the 0 comes from the GPU reject
    same_gpu = laptop(link="https://example.test/c", site_id="[C]", gpu_model="rtx 2050")
    assert ProductMatching.similarity_score(rtx2050, same_gpu, "Pc_Portable_Gamer") >= ProductMatching.MATCH_THRESHOLD
    assert ProductMatching.similarity_score(rtx2050, rtx3050, "Pc_Portable_Gamer") == 0


def test_assign_one_to_one():
    scored = [(90, "a", "x"), (85, "b", "x"), (80, "b", "y")]
    assert ProductMatching.assign_one_to_one(scored) == {"a": ("x", 90), "b": ("y", 80)}


def test_assign_one_to_one_tie_break():
    scored = [(80, "a", "x"), (80, "b", "x")]
    # Without a tie-break, equal scores go by link; the tie-break comes first when given
    assert ProductMatching.assign_one_to_one(scored) == {"a": ("x", 80)}
    assert ProductMatching.assign_one_to_one(scored, lambda t, s: (t != "b",)) == {"b": ("x", 80)}


def test_windows_bundle_rejected():
    plain = laptop()
    bundle = laptop(title=plain["title"] + " / Windows 11 Pro", link="https://example.test/b", site_id="[B-W11P]")
    # Mytek marks the bundle only in its ref
    store_bundle = laptop(link="https://example.test/c", site_id="[BU-C-W11P]")
    store_plain = laptop(link="https://example.test/d", site_id="[D]")
    assert ProductMatching.windows_bundle(bundle) and ProductMatching.windows_bundle(store_bundle)
    assert not ProductMatching.windows_bundle(plain)
    # Tunisianet's '-W' / '-WW' ref segment; a W inside a manufacturer part number is not one
    desktop = {"title": "Pc de bureau Gamer ELITE / Ryzen 5 5500 / RTX 5060 8G / 32 Go", "site_id": "[ELITE-735-32G-W]"}
    assert ProductMatching.windows_bundle(desktop)
    assert ProductMatching.windows_bundle({**desktop, "site_id": "[ELITE-743-32G-SS-WW]"})
    assert not ProductMatching.windows_bundle({**desktop, "site_id": "[ELITE-735-32G]"})
    assert not ProductMatching.windows_bundle({"title": "ASUS TUF A15 / Windows 11", "site_id": "[FA506NFR-HN005W-16G]"})
    assert ProductMatching.similarity_score(plain, store_bundle, "Pc_Portable_Gamer") == 0
    assert ProductMatching.similarity_score(bundle, store_plain, "Pc_Portable_Gamer") == 0
    assert ProductMatching.similarity_score(bundle, store_bundle, "Pc_Portable_Gamer") >= ProductMatching.MATCH_THRESHOLD
    assert ProductMatching.similarity_score(plain, store_plain, "Pc_Portable_Gamer") >= ProductMatching.MATCH_THRESHOLD


def desktop(**overrides):
    product = {
        "title": "Pc de bureau Gamer ELITE / i7-12700F / RTX 5070 12G / 32 Go", "link": "https://example.test/t",
        "site_id": "[ELITE-780-32G]", "price": 4039, "cpu_brand": "Intel", "cpu_model": "i7-12700f", "cpu_cores": None,
        "ram_size": 32, "ram_type": "ddr4", "gpu_brand": None, "gpu_model": "rtx-5070", "gpu_memory": 12,
        "storage_type": "ssd", "storage_size": 1024,
    }
    product.update(overrides)
    return product


def test_desktop_ram_type_rejected():
    mytek = desktop(title="Pc de Bureau Gamer MYTEK i7 12è Gén 32Go RTX5070 12G", link="https://example.test/m",
                    site_id="[ALIEN-12700-5070]", price=4699, ram_size=None, gpu_brand="nvidia", gpu_memory=None)
    ddr5 = desktop(title="Pc de bureau Gamer ELITE / i7-12700F / RTX 5070 12G / 32 Go DDR5", site_id="[ELITE-780-32G-DDR5]",
                   ram_type="ddr5")
    assert ProductMatching.similarity_score(desktop(), mytek, "Pc_Bureau_Gamer") >= ProductMatching.MATCH_THRESHOLD
    assert ProductMatching.similarity_score(ddr5, mytek, "Pc_Bureau_Gamer") == 0


def test_match_store_prefers_closest_price():
    # Two Tunisianet listings of the same laptop score the same against one store listing
    cheap = laptop(link="https://example.test/a", site_id="[A]", price=2124)
    equal = laptop(link="https://example.test/b", site_id="[B]", price=2229)
    store = laptop(link="https://example.test/x", site_id="[X]", price=2229)
    matches = ProductMatching.match_store([cheap, equal], [store], "Pc_Portable_Gamer")
    assert {link: store_link for link, (store_link, _) in matches.items()} == {"https://example.test/b": "https://example.test/x"}


# The DB checks run on a fresh build from the CSVs and on the committed tunicompare.db, which Vercel serves
@pytest.fixture(params=["built", "committed"])
def db_path(request):
    if request.param == "built":
        return request.getfixturevalue("built_db")
    return DB_PATH


def test_db_no_store_listing_reused(db_path):
    with sqlite3.connect(db_path) as conn:
        for type_ in TYPES:
            for column in STORE_COLUMNS.values():
                reused = conn.execute(
                    f"SELECT {column}, COUNT(*) FROM matched_{type_} WHERE {column} IS NOT NULL "
                    f"GROUP BY {column} HAVING COUNT(*) > 1").fetchall()
                assert reused == [], f"matched_{type_}.{column}: {len(reused)} store listings matched more than once"


@pytest.mark.parametrize("type_", ["pc_portable_gamer", "pc_bureau_gamer"])
def test_db_pairs_agree_on_known_specs(db_path, type_):
    conflicts = []
    with sqlite3.connect(db_path) as conn:
        for store, column in STORE_COLUMNS.items():
            rows = conn.execute(f"""
                SELECT t.title, s.title, t.gpu_model, s.gpu_model, t.ram_size, s.ram_size
                FROM matched_{type_} m
                JOIN tunisianet_{type_} t ON t.link = m.linktunisianet
                JOIN {store}_{type_} s ON s.link = m.{column}""").fetchall()
            for title, store_title, gpu, store_gpu, ram, store_ram in rows:
                if gpu and store_gpu and ProductMatching.normalize_gpu(gpu) != ProductMatching.normalize_gpu(store_gpu):
                    conflicts.append(("gpu", title, store_title))
                if ram is not None and store_ram is not None and ram != store_ram:
                    conflicts.append(("ram", title, store_title))
    assert conflicts == []


@pytest.mark.parametrize("type_", ["pc_portable_gamer", "pc_bureau_gamer"])
def test_db_no_windows_bundle_mismatch(db_path, type_):
    # A PC sold with a Windows licence is a different offer from the same PC without one
    mismatches = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        for store, column in STORE_COLUMNS.items():
            rows = conn.execute(f"""
                SELECT t.title, t.site_id, s.title AS store_title, s.site_id AS store_site_id
                FROM matched_{type_} m
                JOIN tunisianet_{type_} t ON t.link = m.linktunisianet
                JOIN {store}_{type_} s ON s.link = m.{column}""").fetchall()
            for row in rows:
                tunisianet = {"title": row["title"], "site_id": row["site_id"]}
                other = {"title": row["store_title"], "site_id": row["store_site_id"]}
                if ProductMatching.windows_bundle(tunisianet) != ProductMatching.windows_bundle(other):
                    mismatches.append((row["site_id"], row["store_site_id"]))
    assert mismatches == []


# The summer-2025 snapshot as first committed. tunicompare.db is byte-identical from 2f9c1ad to this commit
# (on main), and only the matched_* tables may change after it. Comparing against HEAD instead would compare a
# committed rebuild with itself.
SNAPSHOT_COMMIT = "8264fe5"


@pytest.fixture
def snapshot_db(tmp_path):
    shown = subprocess.run(["git", "show", f"{SNAPSHOT_COMMIT}:tunicompare.db"], cwd=REPO_ROOT, capture_output=True)
    if shown.returncode != 0:
        pytest.skip(f"tunicompare.db not available at {SNAPSHOT_COMMIT}")
    path = tmp_path / "snapshot.db"
    path.write_bytes(shown.stdout)
    return path


def snapshot(path, table):
    with sqlite3.connect(path) as conn:
        return conn.execute(f"SELECT link, title, price FROM {table} ORDER BY link").fetchall()


def test_snapshot_prices_unchanged(db_path, snapshot_db):
    # The prices are the summer-2025 snapshot: rebuilding the pairings must not touch them
    for site in SITES:
        for type_ in TYPES:
            table = f"{site}_{type_}"
            assert snapshot(db_path, table) == snapshot(snapshot_db, table), table
