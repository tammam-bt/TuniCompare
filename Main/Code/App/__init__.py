from flask import Flask, render_template
import os


app = Flask(__name__)



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


if __name__ == "__main__":
    app.run(debug=True)