from sqlalchemy import Column, Integer, String, Float, DateTime

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CartMock(Base):
    """
    DataBase structure of our shopping cart
    """

    __tablename__ = "Cart"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    date_created = Column(DateTime, default=datetime.utcnow())

    def __init__(self, name, quantity, price):
        self.name = name
        self.quantity = quantity
        self.price = price

    def __eq__(self, other):
        return (
            isinstance(other, CartMock)
            and self.name == other.name
            and self.price == other.price
            and self.quantity == other.quantity
        )


class MarketItemMock(Base):
    """
    DataBase structure of our market stock
    """

    __tablename__ = "MarketItem"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __eq__(self, other):
        return (
            isinstance(other, MarketItemMock)
            and self.name == other.name
            and self.price == other.price
        )
