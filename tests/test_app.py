import importlib
import os
import shutil

import pytest

PRODUCT_COUNTS = [("pc_portable_gamer", 250), ("pc_bureau_gamer", 525), ("ecran_gamer", 32)]


@pytest.fixture
def make_client(monkeypatch):
    # app.py reads TUNICOMPARE_DB at import time, so each client reloads the module
    def _make(db_path):
        monkeypatch.setenv("TUNICOMPARE_DB", str(db_path))
        import app as app_module
        return importlib.reload(app_module).app.test_client()
    return _make


@pytest.fixture
def client(make_client, built_db):
    return make_client(built_db)


def load(client, product_type, limit=None, offset=None):
    query = f"/load_products?product_type={product_type}"
    if limit is not None:
        query += f"&limit={limit}"
    if offset is not None:
        query += f"&offset={offset}"
    return client.get(query)


@pytest.mark.parametrize("path", ["/", "/shop/laptop", "/shop/desktop", "/shop/screen"])
def test_pages_render(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("path", ["/static/CSS/shop.css", "/static/JS/product-list.js", "/static/Resources/Logo.png"])
def test_static_served(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("product_type,count", PRODUCT_COUNTS)
def test_load_products_counts(client, product_type, count):
    response = load(client, product_type, limit=1000, offset=0)
    assert response.status_code == 200
    products = response.get_json()
    assert len(products) == count
    for product in products:
        assert set(product) == {"tunisianet", "mytek", "scoopgaming"}
        assert set(product["tunisianet"]) == {"link", "title", "image", "price"}
    prices = [product["tunisianet"]["price"] for product in products]
    assert prices == sorted(prices)


def test_default_paging(client):
    first_page = load(client, "pc_portable_gamer").get_json()
    everything = load(client, "pc_portable_gamer", limit=1000).get_json()
    assert len(first_page) == 5
    assert first_page == everything[:5]


def test_offset_past_end_is_empty(client):
    response = load(client, "pc_portable_gamer", limit=5, offset=10000)
    assert response.status_code == 200
    assert response.get_json() == []


def test_missing_db_returns_503(make_client, tmp_path):
    client = make_client(tmp_path / "nope.db")
    assert client.get("/").status_code == 200
    response = load(client, "pc_portable_gamer")
    assert response.status_code == 503
    assert response.get_json() == {"error": "Database unavailable"}


def test_read_only_db_serves(make_client, built_db, tmp_path):
    # Vercel's filesystem is read-only: the app must not need to write next to the database
    directory = tmp_path / "read only"
    directory.mkdir()
    path = directory / "tunicompare.db"
    shutil.copy(built_db, path)
    os.chmod(path, 0o444)
    os.chmod(directory, 0o555)
    try:
        response = load(make_client(path), "ecran_gamer", limit=1000)
        assert response.status_code == 200
        assert len(response.get_json()) == 32
        assert os.listdir(directory) == ["tunicompare.db"]
    finally:
        os.chmod(directory, 0o755)
        os.chmod(path, 0o644)
