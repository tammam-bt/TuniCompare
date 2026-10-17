# Builds tunicompare.db from the committed CSVs in Main/Products, without scraping.
# Usage: python -m Scripts.build_db
from Scripts import DB, ProductMatching
from Scripts.DB import DB_PATH


def main(db_path=DB_PATH):
    DB.main(db_path)
    ProductMatching.main(db_path)


if __name__ == "__main__":
    main()
