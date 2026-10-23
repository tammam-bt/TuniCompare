# Measures how often the pairs in the matched_* tables are really the same product,
# using the hand labels in docs/matching-labels.csv.
#
# Usage (from the repo root):
#   python -m Scripts.eval_matching                       # every pair in tunicompare.db
#   python -m Scripts.eval_matching --db old.db --sample 40
#       # a fixed random sample of 40 pairs per category (seed SAMPLE_SEED); categories with
#       # 40 pairs or fewer are evaluated in full
#   python -m Scripts.eval_matching --unlabelled          # list the pairs that still need a label
#
# Label columns: category, tunisianet_link, store, store_link, same, note.
# same = 1 when both listings are the same product, or the same SKU in every spec
# (a different colour or keyboard layout still counts). Unsure pairs are labelled 0 with a note.
import argparse
import csv
import os
import random
import sqlite3
from pathlib import Path

from Scripts.DB import DB_PATH, REPO_ROOT

LABELS_PATH = os.path.join(REPO_ROOT, "docs", "matching-labels.csv")
CATEGORIES = ["pc_portable_gamer", "pc_bureau_gamer", "ecran_gamer"]
STORES = {"mytek": "linkmytek", "scoopgaming": "linkscoopgaming"}
SAMPLE_SEED = 5

# Spec columns shown next to the titles when listing unlabelled pairs
SPEC_COLUMNS = {
    "pc_portable_gamer": ["cpu_model", "ram_size", "storage_size", "gpu_model", "screen_size", "screen_refresh_rate"],
    "pc_bureau_gamer": ["cpu_model", "ram_size", "storage_size", "gpu_model", "gpu_memory"],
    "ecran_gamer": ["brand", "panel_type", "size", "resolution", "refresh_rate"],
}


def connect_read_only(db_path):
    return sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)


def db_pairs(conn, category):
    """Every (tunisianet_link, store, store_link) pair in matched_<category>, sorted."""
    pairs = []
    for store, column in STORES.items():
        rows = conn.execute(f"SELECT linktunisianet, {column} FROM matched_{category} WHERE {column} IS NOT NULL")
        pairs += [(tunisianet_link, store, store_link) for tunisianet_link, store_link in rows]
    return sorted(pairs)


def sample_pairs(pairs, size=None, seed=SAMPLE_SEED):
    if size is None or len(pairs) <= size:
        return list(pairs)
    return sorted(random.Random(seed).sample(pairs, size))


def load_labels(path=LABELS_PATH):
    labels = {}
    if not os.path.exists(path):
        return labels
    with open(path, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            key = (row["category"], row["tunisianet_link"], row["store"], row["store_link"])
            labels[key] = int(row["same"])
    return labels


def evaluate(db_path=DB_PATH, labels=None, sample=None):
    """Per category: match counts per store and the precision of the labelled pairs among those evaluated."""
    labels = load_labels() if labels is None else labels
    results = {}
    with connect_read_only(db_path) as conn:
        for category in CATEGORIES:
            pairs = db_pairs(conn, category)
            chosen = sample_pairs(pairs, sample)
            stores = {}
            for store, column in STORES.items():
                used, distinct = conn.execute(
                    f"SELECT COUNT({column}), COUNT(DISTINCT {column}) FROM matched_{category}").fetchone()
                store_pairs = [pair for pair in chosen if pair[1] == store]
                judged = [labels[(category, *pair)] for pair in store_pairs if (category, *pair) in labels]
                stores[store] = {"matches": used, "distinct": distinct, "evaluated": len(store_pairs),
                                 "labelled": len(judged), "same": sum(judged)}
            judged = [labels[(category, *pair)] for pair in chosen if (category, *pair) in labels]
            results[category] = {
                "matches": len(pairs),
                "evaluated": len(chosen),
                "labelled": len(judged),
                "same": sum(judged),
                "precision": sum(judged) / len(judged) if judged else None,
                "unlabelled": [pair for pair in chosen if (category, *pair) not in labels],
                "stores": stores,
            }
    return results


def describe(conn, site, category, link):
    columns = ["title", "price"] + SPEC_COLUMNS[category]
    row = conn.execute(f"SELECT {', '.join(columns)} FROM {site}_{category} WHERE link = ?", (link,)).fetchone()
    title, price, *specs = row
    return f"{title} | {price} DT | " + ", ".join(f"{name}={value}" for name, value in zip(SPEC_COLUMNS[category], specs))


def print_report(results, db_path, sample):
    scope = f"fixed sample of {sample} pairs per category (seed {SAMPLE_SEED})" if sample else "every pair"
    print(f"DB: {db_path}  |  evaluated: {scope}")
    for category, result in results.items():
        precision = "n/a" if result["precision"] is None else f"{result['precision']:.2f}"
        print(f"\n{category}: {result['matches']} matched pairs, precision {precision} "
              f"({result['same']}/{result['labelled']} labelled pairs are the same product, "
              f"{len(result['unlabelled'])} of {result['evaluated']} evaluated pairs unlabelled)")
        for store, counts in result["stores"].items():
            store_precision = f"{counts['same'] / counts['labelled']:.2f}" if counts["labelled"] else "n/a"
            print(f"  {store:<12} {counts['matches']:>4} matches, {counts['distinct']:>4} distinct listings, "
                  f"{counts['matches'] - counts['distinct']:>4} reused  |  precision {store_precision} "
                  f"({counts['same']}/{counts['labelled']})")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Precision of the matched_* pairs against hand labels")
    parser.add_argument("--db", default=DB_PATH, help="SQLite DB to evaluate (default: tunicompare.db)")
    parser.add_argument("--labels", default=LABELS_PATH, help="labels CSV (default: docs/matching-labels.csv)")
    parser.add_argument("--sample", type=int, help="evaluate a fixed random sample of this many pairs per category")
    parser.add_argument("--unlabelled", action="store_true", help="list the evaluated pairs that have no label")
    args = parser.parse_args(argv)

    results = evaluate(args.db, load_labels(args.labels), args.sample)
    if args.unlabelled:
        with connect_read_only(args.db) as conn:
            for category, result in results.items():
                for tunisianet_link, store, store_link in result["unlabelled"]:
                    print(f"[{category}] {store}")
                    print(f"  T: {describe(conn, 'tunisianet', category, tunisianet_link)}")
                    print(f"  S: {describe(conn, store, category, store_link)}")
                    print(f"  {category},{tunisianet_link},{store},{store_link}")
        return
    print_report(results, args.db, args.sample)


if __name__ == "__main__":
    main()
