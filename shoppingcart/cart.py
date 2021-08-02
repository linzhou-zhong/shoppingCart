import logging

from cart_abc import ShoppingCart
from utils import convert_currency
from flask_sqlalchemy import SQLAlchemy, Model


class MyShoppingCart(ShoppingCart):
    def __init__(self, session: SQLAlchemy, cart_class: Model, market_class: Model):
        self._session = session
        self._cart_class = cart_class
        self._market_class = market_class

    def add_item(self, product_code: str, quantity: int):
        """
        Add and registry item information to SQL database
        :argument
            :param product_code: Name of item
            :param quantity: Number of item
        :raise: Exception if cannot add data to SQL database
        """
        try:
            price = (
                self._session.query(self._market_class)
                .filter(self._market_class.name == product_code)
                .first()
                .price
            )
            cart = self._cart_class(name=product_code, quantity=quantity, price=price)
            self._session.add(cart)
            self._session.commit()

        except Exception as e:
            raise Exception(f"Their was an issue adding your new product: {e}")

    def print_receipt(self, currency_type="EUR") -> [SQLAlchemy, float]:
        """
        Print out the shopping cart's all items information and total spending
        ":argument
            :param currency_type: Type of currency of receipt
        :return: list of items, total spending
        """
        products_cart = (
            self._session.query(self._cart_class)
            .order_by(self._cart_class.date_created)
            .all()
        )
        total = 0.0

        for p in products_cart:
            p.price = round(convert_currency(p.price, currency_type) * p.quantity, 2)
            total += p.price

        return products_cart, total

    def remove_item(self, item_id: int):
        """
        Remove a specific item from shopping cart
        :argument
            :param item_id: Order of ID in which item will be removed
        :raise: Exception if we cannot remove the item from shopping cart
        """
        item_to_delete = self._session.query(self._cart_class).get_or_404(item_id)

        try:
            self._session.delete(item_to_delete)
            self._session.commit()

        except Exception as e:
            raise Exception(f"Their was an issue removing the item: {e}")

    def update_item(self, item_name: int, item_new_price: float):
        """
        Update a specific item's price, meanwhile update MySQL database
        :argument
            :param item_name: Name of item
            :param item_new_price: New price to place its previous price
        :raise: Exception if we cannot update the item's price
        """
        try:
            item = (
                self._session.query(self._market_class)
                .filter(self._market_class.name == item_name)
                .first()
            )
            if item is None:
                logging.warning(f"{item_name} cannot be found in DB")
                return
            item.price = item_new_price
            self._session.commit()
            logging.info(f"{item_name} price has been updated in DB")

        except Exception as e:
            raise Exception(f"Their was an issue updating the item: {e}")
