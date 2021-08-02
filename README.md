# Shopping cart

## Component of  Shopping Cart
1. **RestAPI**: Flask
2. **Distributed message & message-broker**: Celery, RabbitMQ
3. **SQL**: MySQL
4. **Object-Relational Mapper**: SQLAlchemy

## Create Virtual Environment
```shell
python -m venv venv
source venv/bin/active
pip install -r blueface/requirements.txt
```

## Install RabbitMQ
```shell
brew update
brew install rabbitmq
```
if rabbitmq is not found when you try to run in terminal, please add it to your PATH.
```shell
export PATH=$PATH:/usr/local/sbin
```

## Run RabbitMQ as Broker
```shell
sudo rabbitmq-server
```
![Alt Text](https://i.imgflip.com/5idg9h.gif)

## Run Celery as Asynchronous Task Queue
Make sure that you are currently in **blueface/shoppingcart** folder.
```shell
celery -A app.celery worker --loglevel=info
```
![Alt Text](https://i.imgflip.com/5idhzx.gif)

## Initialize MySQL database

Make sure that you are in **blueface/shoppingcart** folder.
```shell
python3
```
```python
from app import create_db
create_db()
```

Add those items in market_item table.

```sql
insert into market_item (name, price)
VALUES ('apple', 1.0),
       ('banana', 2.5),
       ('milk', 3.0),
       ('pen', 1.0),
       ('book', 19.98)
```
A `test.db` file will be generated eventually.

I've already generated `test.db` for this project so you can ignore this part.


## Run Application
Make sure that you are still in **blueface/shoppingcart** folder.
```shell
python3 -m app
```
![Alt Text](https://i.imgflip.com/5idiy7.gif)

Now, you can access shopping cart by visiting [localhost:5000]() from the navigator.

## Add item in the shopping cart
You can easily add all listed products in your shopping cart.

![Alt Text](https://i.imgflip.com/5idjqg.gif)

Shopping cart page is redirected by `app.route("/")` with **GET** method.

Adding action is triggered by `app.route("/")` with **POST** method.

```python
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
```

## Change type of currency
You are also allowed to convert the receipt in different currency (**EUR, USD, GBP, CNY**)

![Alt Text](https://i.imgflip.com/5idkag.gif)

The default currency is `EUR`.

Changing action is triggered by `@app.route("/cart")` with **POST** method.
```python
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
```
## Remove item in the shopping cart
You can directly delete any item in the shopping cart.

![Alt Text](https://i.imgflip.com/5idqws.gif)

Deleting action is triggered by `@app.route("/delete/<item_id>/<currenyType>")` where `item_id` is the order in which item is added.

```python
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
```

## Update the price of item

You can use **Postman** to send your request in order to update the price of item.

![Alt Text](https://i.imgflip.com/5idnmn.gif)

Updating action is triggered by `@app.route("/update")` with **POST** method.

```python
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
```

## Author
- [Linzhou ZHONG](https://github.com/linzhou-zhong)
- [Medium](https://justgiveacar.medium.com)

