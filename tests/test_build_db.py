import shutil
import sqlite3

from Scripts import build_db

SITES = ["tunisianet", "mytek", "scoopgaming"]
TYPES = ["pc_portable_gamer", "pc_bureau_gamer", "ecran_gamer"]

# CSV lines minus the header, for the summer-2025 snapshot in Main/Products
EXPECTED_ROWS = {
    "tunisianet_pc_portable_gamer": 250,
    "tunisianet_pc_bureau_gamer": 525,
    "tunisianet_ecran_gamer": 32,
    "mytek_pc_portable_gamer": 221,
    "mytek_pc_bureau_gamer": 156,
    "mytek_ecran_gamer": 25,
    "scoopgaming_pc_portable_gamer": 41,
    "scoopgaming_pc_bureau_gamer": 2,
    "scoopgaming_ecran_gamer": 26,
    # One matched row per Tunisianet product
    "matched_pc_portable_gamer": 250,
    "matched_pc_bureau_gamer": 525,
    "matched_ecran_gamer": 32,
}


def table_names(conn):
    return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def row_counts(path):
    with sqlite3.connect(path) as conn:
        return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in EXPECTED_ROWS}


def test_tables_are_lowercase(built_db):
    expected = {f"{site}_{type_}" for site in SITES for type_ in TYPES} | {f"matched_{type_}" for type_ in TYPES}
    with sqlite3.connect(built_db) as conn:
        assert table_names(conn) == expected


def test_row_counts(built_db):
    assert row_counts(built_db) == EXPECTED_ROWS


def test_matched_columns_lowercase(built_db):
    with sqlite3.connect(built_db) as conn:
        for type_ in TYPES:
            columns = [row[1] for row in conn.execute(f"PRAGMA table_info(matched_{type_})")]
            assert columns == ["linktunisianet", "linkmytek", "linkscoopgaming"]


def test_matched_foreign_keys_lowercase(built_db):
    with sqlite3.connect(built_db) as conn:
        names = table_names(conn)
        for type_ in TYPES:
            referenced = [row[2] for row in conn.execute(f"PRAGMA foreign_key_list(matched_{type_})")]
            assert sorted(referenced) == sorted(f"{site}_{type_}" for site in SITES)
            assert all(table in names for table in referenced)


def test_rebuild_is_idempotent(built_db, tmp_path):
    path = tmp_path / "rebuilt.db"
    shutil.copy(built_db, path)
    build_db.main(str(path))
    assert row_counts(path) == EXPECTED_ROWS
