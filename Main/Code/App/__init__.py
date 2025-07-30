from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("dburl")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


with app.app_context():
    # automap base to reflect existing database tables
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)
    # Convert tables to classes
    Matched_Pc_Portable_Gamer = Base.classes.matched_pc_portable_gamer
    Matched_Pc_Bureau_Gamer = Base.classes.matched_pc_bureau_gamer
    Matched_Ecran_Gamer = Base.classes.matched_ecran_gamer
    Tunisianet_Pc_Portable_Gamer = Base.classes.tunisianet_pc_portable_gamer
    Tunisianet_Pc_Bureau_Gamer = Base.classes.tunisianet_pc_bureau_gamer
    Tunisianet_Ecran_Gamer = Base.classes.tunisianet_ecran_gamer
    Mytek_Pc_Portable_Gamer = Base.classes.mytek_pc_portable_gamer
    Mytek_Pc_Bureau_Gamer = Base.classes.mytek_pc_bureau_gamer
    Mytek_Ecran_Gamer = Base.classes.mytek_ecran_gamer
    ScoopGaming_Pc_Portable_Gamer = Base.classes.scoopgaming_pc_portable_gamer
    ScoopGaming_Pc_Bureau_Gamer = Base.classes.scoopgaming_pc_bureau_gamer
    ScoopGaming_Ecran_Gamer = Base.classes.scoopgaming_ecran_gamer

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
    products = session.query(
        Matched_Pc_Portable_Gamer if product_type == "pc_portable_gamer" 
        else Matched_Pc_Bureau_Gamer if product_type == "pc_bureau_gamer" 
        else Matched_Ecran_Gamer
    ).join(Tunisianet_Pc_Portable_Gamer if product_type == "pc_portable_gamer" else Tunisianet_Pc_Bureau_Gamer if product_type == "pc_bureau_gamer" else Tunisianet_Ecran_Gamer).order_by(
        (Tunisianet_Pc_Portable_Gamer.price if product_type == "pc_portable_gamer" 
        else Tunisianet_Pc_Bureau_Gamer.price if product_type == "pc_bureau_gamer" 
        else Tunisianet_Ecran_Gamer.price).asc()
    ).limit(limit).offset(offset).all()
    for product in products:
        product_dict = {"tunisianet" : get_product(session, Tunisianet_Pc_Portable_Gamer if product_type == "pc_portable_gamer" else Tunisianet_Pc_Bureau_Gamer if product_type == "pc_bureau_gamer" else Tunisianet_Ecran_Gamer, product.linktunisianet, "tunisianet") if product.linktunisianet else None,
                        "mytek" : get_product(session, Mytek_Pc_Portable_Gamer if product_type == "pc_portable_gamer" else Mytek_Pc_Bureau_Gamer if product_type == "pc_bureau_gamer" else Mytek_Ecran_Gamer, product.linkmytek, "mytek") if product.linkmytek else None,
                        "scoopgaming" : get_product(session, ScoopGaming_Pc_Portable_Gamer if product_type == "pc_portable_gamer" else ScoopGaming_Pc_Bureau_Gamer if product_type == "pc_bureau_gamer" else ScoopGaming_Ecran_Gamer, product.linkscoopgaming, "scoopgaming") if product.linkscoopgaming else None}
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
    session = Session(db.engine)
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    product_type = request.args.get("product_type", default="pc_portable_gamer", type=str)
    products = get_products(session=session, product_type=product_type, limit=limit, offset=offset)
    session.close()
    return jsonify(products)
if __name__ == "__main__":
    app.run(debug=True)