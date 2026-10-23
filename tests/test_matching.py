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


@pytest.fixture
def head_db(tmp_path):
    shown = subprocess.run(["git", "show", "HEAD:tunicompare.db"], cwd=REPO_ROOT, capture_output=True)
    if shown.returncode != 0:
        pytest.skip("no tunicompare.db in git HEAD")
    path = tmp_path / "head.db"
    path.write_bytes(shown.stdout)
    return path


def snapshot(path, table):
    with sqlite3.connect(path) as conn:
        return conn.execute(f"SELECT link, title, price FROM {table} ORDER BY link").fetchall()


def test_snapshot_prices_unchanged(db_path, head_db):
    # The prices are the summer-2025 snapshot: rebuilding the pairings must not touch them
    for site in SITES:
        for type_ in TYPES:
            table = f"{site}_{type_}"
            assert snapshot(db_path, table) == snapshot(head_db, table), table
