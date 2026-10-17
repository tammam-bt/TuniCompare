from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from pathlib import Path
import os
import sqlite3


# Built from the CSVs by `python -m Scripts.build_db` and committed alongside the app
DB_PATH = os.path.abspath(os.getenv("TUNICOMPARE_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tunicompare.db")))

def connect_read_only():
    # Vercel's filesystem is read-only, so the database is opened read-only and never written to
    return sqlite3.connect(Path(DB_PATH).as_uri() + "?mode=ro&immutable=1", uri=True, check_same_thread=False)

# Vercel serves public/** from its CDN, so static files live in public/static and keep their /static URLs
app = Flask(__name__, static_folder="public/static", static_url_path="/static")
# A file URL makes SQLAlchemy give each thread its own connection; "sqlite://" would share one across
# concurrent requests. The URL only picks the pool, connections still come from connect_read_only.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"creator": connect_read_only}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Table classes are reflected lazily on first DB request instead of at import
# time, so an unreachable database doesn't stop the app from booting.
_models = {}

def get_models():
    if not _models:
        Base = automap_base()
        Base.prepare(autoload_with=db.engine)
        _models.update({
            "matched_pc_portable_gamer": Base.classes.matched_pc_portable_gamer,
            "matched_pc_bureau_gamer": Base.classes.matched_pc_bureau_gamer,
            "matched_ecran_gamer": Base.classes.matched_ecran_gamer,
            "tunisianet_pc_portable_gamer": Base.classes.tunisianet_pc_portable_gamer,
            "tunisianet_pc_bureau_gamer": Base.classes.tunisianet_pc_bureau_gamer,
            "tunisianet_ecran_gamer": Base.classes.tunisianet_ecran_gamer,
            "mytek_pc_portable_gamer": Base.classes.mytek_pc_portable_gamer,
            "mytek_pc_bureau_gamer": Base.classes.mytek_pc_bureau_gamer,
            "mytek_ecran_gamer": Base.classes.mytek_ecran_gamer,
            "scoopgaming_pc_portable_gamer": Base.classes.scoopgaming_pc_portable_gamer,
            "scoopgaming_pc_bureau_gamer": Base.classes.scoopgaming_pc_bureau_gamer,
            "scoopgaming_ecran_gamer": Base.classes.scoopgaming_ecran_gamer,
        })
    return _models

def best_price(product_type, product):
    """
    Returns the best price for a given product type and product.
    """
    if product_type == "pc_portable_gamer":
        return min(product["tunisianet"]["price"], product["mytek"]["price"], product["scoopgaming"]["price"])
    elif product_type == "pc_bureau_gamer":
        return min(product["tunisianet"]["price"], product["mytek"]["price"], product["scoopgaming"]["price"])
    elif product_type == "ecran_gamer":
        return min(product["tunisianet"]["price"], product["mytek"]["price"], product["scoopgaming"]["price"])
    else:
        raise ValueError("Invalid product type specified.")

def get_product(session, Table, link_, website):
    if website == "tunisianet":
        result = session.query(Table.link, Table.title, Table.image, Table.price).filter_by(link=link_).first()
        dict_ = dict(result._mapping) if result else None
    elif website == "mytek":
        result = session.query(Table.link, Table.price).filter_by(link=link_).first()
        dict_ = dict(result._mapping) if result else None
    elif website == "scoopgaming":
        result = session.query(Table.link, Table.price).filter_by(link=link_).first()
        dict_ = dict(result._mapping) if result else None
    return dict_

def get_products(session, product_type, limit=5, offset=0):
    final_products = []
    assert product_type in ["pc_portable_gamer", "pc_bureau_gamer", "ecran_gamer"], "Invalid product type specified."
    models = get_models()
    Matched = models[f"matched_{product_type}"]
    Tunisianet = models[f"tunisianet_{product_type}"]
    Mytek = models[f"mytek_{product_type}"]
    ScoopGaming = models[f"scoopgaming_{product_type}"]
    products = session.query(Matched).join(Tunisianet).order_by(
        Tunisianet.price.asc()
    ).limit(limit).offset(offset).all()
    for product in products:
        product_dict = {"tunisianet" : get_product(session, Tunisianet, product.linktunisianet, "tunisianet") if product.linktunisianet else None,
                        "mytek" : get_product(session, Mytek, product.linkmytek, "mytek") if product.linkmytek else None,
                        "scoopgaming" : get_product(session, ScoopGaming, product.linkscoopgaming, "scoopgaming") if product.linkscoopgaming else None}
        final_products.append(product_dict)
    return final_products

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/shop/desktop", methods=["GET"])
def shop_desktop():
    return render_template("shop/desktop.html")

@app.route("/shop/laptop", methods=["GET"])
def shop_laptop():
    return render_template("shop/laptop.html")

@app.route("/shop/screen", methods=["GET"])
def shop_screen():
    return render_template("shop/screen.html")

@app.route("/load_products", methods=["GET"])
def load_products():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    product_type = request.args.get("product_type", default="pc_portable_gamer", type=str)
    session = Session(db.engine)
    try:
        products = get_products(session=session, product_type=product_type, limit=limit, offset=offset)
    except OperationalError:
        app.logger.exception("Database unavailable")
        return jsonify({"error": "Database unavailable"}), 503
    finally:
        session.close()
    return jsonify(products)
if __name__ == "__main__":
    app.run(debug=True)