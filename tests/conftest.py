import pytest

from Scripts import build_db


@pytest.fixture(scope="session")
def built_db(tmp_path_factory):
    # The directory name contains a space, like the owner's "VS Code Projects" checkout
    path = tmp_path_factory.mktemp("db dir") / "tunicompare.db"
    build_db.main(str(path))
    return str(path)
