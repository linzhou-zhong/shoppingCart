import json
from flask import Flask, request, render_template, url_for, redirect
from cart import MyShoppingCart
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from celery import Celery

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["CELERY_BROKER_URL"] = "amqp://guest@localhost//"
app.config["CELERY_RESULT_BACKEND"] = "rpc://"

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

db = SQLAlchemy(app)


class Cart(db.Model):
    """
    DataBase structure of our shopping cart
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())


class MarketItem(db.Model):
    """
    DataBase structure of our market stock
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)


db.create_all()

shoppingCart = MyShoppingCart(
    session=db.session, cart_class=Cart, market_class=MarketItem
)


@app.route("/", methods=["GET", "POST"])
def main():
    """
    Get all items from market store if request == GET,
    otherwise add a new item into our shopping cart where request == POST
    :return: flask static page template
    """
    if request.method == "POST":
        name = request.form.get("items")
        quantity = request.form["product_quantity"]
        res = to_add_item.delay(name, quantity)
        while res.state == "PENDING":
            continue
        return redirect("/cart")

    else:
        market_item = MarketItem.query.order_by(MarketItem.id).all()
        return render_template("index.html", marketItem=market_item)


@app.route("/cart", defaults={"currency_type": "EUR"}, methods=["GET", "POST"])
@app.route("/cart/<currency_type>", methods=["GET"])
def receipt(currency_type):
    """
    Get all your items inside of shopping cart and you can get your receipt in different currency
    :argument
        :param currency_type: Type of currency, I've provided these four types: EUR, USD, GBP and CNY
    :return: flask static page template
    """
    if request.method == "GET":
        products_cart, total = shoppingCart.print_receipt(currency_type)

        return render_template(
            "cart.html",
            products=products_cart,
            currenyType=currency_type,
            total=round(total, 2),
        )

    else:
        currency_type = request.form.get("currency_type")
        products_cart, total = shoppingCart.print_receipt(currency_type)

        return render_template(
            "cart.html",
            products=products_cart,
            currenyType=request.form.get("currency_type"),
            total=round(total, 2),
        )


@app.route("/delete/<item_id>/<currenyType>")
def remove_item(item_id: int, currenyType: str):
    """
    Remove the items from your shopping cart
    :argument
        :param item_id : int: the number of order in which items are added into shopping cart
        :param currenyType : : Type of currency (EUR, USD, GBP and CNY)
    :return: flask static page template
    """
    res = to_remove_item.delay(item_id)
    while res.state == "PENDING":
        continue
    return redirect(url_for("receipt", currency_type=currenyType))


@app.route("/update", methods=["POST"])
def update_item():
    """
    Update item's price from database by json file
    """
    items_to_update = json.loads(request.data)
    for item in items_to_update.items():
        item_name = item[0]
        item_new_price = item[1]
        shoppingCart.update_item(item_name, item_new_price)

    return f" The price of {[i for i in items_to_update]} have been updated."


@celery.task(bind=True, name="add item", max_retries=2)
def to_add_item(self, name, quantity):
    """
    Celery task: add item into your shopping cart
    :argument
        :param self: celery Class
        :param name: name of item
        :param quantity: number of item
    """
    try:
        shoppingCart.add_item(name, quantity)
    except:
        self.retry()


@celery.task(bind=True, name="remove item", max_retries=2)
def to_remove_item(self, item_id):
    """
    Celery task: remove item from your shopping cart
        :param self:
        :param item_id: The order in which item will be remove
    """
    try:
        shoppingCart.remove_item(item_id)
    except:
        self.retry()


if __name__ == "__main__":
    app.run(debug=True)
