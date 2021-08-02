import sys

sys.path.append("../shoppingcart")

from shoppingcart.cart import MyShoppingCart
from tests.model_mock import CartMock, MarketItemMock
from alchemy_mock.mocking import UnifiedAlchemyMagicMock


def test_add_item():
    db_session_mock = UnifiedAlchemyMagicMock()
    db_session_mock.add(MarketItemMock(name="item_1", price=10))
    shopping_cart = MyShoppingCart(
        db_session_mock, cart_class=CartMock, market_class=MarketItemMock
    )
    shopping_cart.add_item("item_1", 1)
    assert db_session_mock.query(CartMock).filter(name="item_1").first() == CartMock(
        name="item_1", price=10, quantity=1
    )


def test_get_receipt():
    db_session_mock = UnifiedAlchemyMagicMock()
    db_session_mock.add(CartMock(name="item_1", price=10, quantity=1))
    shopping_cart = MyShoppingCart(
        db_session_mock, cart_class=CartMock, market_class=MarketItemMock
    )
    cart, total = shopping_cart.print_receipt()
    assert CartMock(name="item_1", price=10, quantity=1) in cart
    assert total == 10


def test_add_item_with_multiple_quantity():
    db_session_mock = UnifiedAlchemyMagicMock()
    db_session_mock.add(MarketItemMock(name="item_1", price=10))
    shopping_cart = MyShoppingCart(
        db_session_mock, cart_class=CartMock, market_class=MarketItemMock
    )
    shopping_cart.add_item("item_1", 2)
    shopping_cart.add_item("item_1", 5)
    assert db_session_mock.query(CartMock).filter(CartMock.name == "item_1").all()[
        -1
    ] == CartMock(name="item_1", price=10, quantity=5)


def test_add_different_items():
    db_session_mock = UnifiedAlchemyMagicMock()
    db_session_mock.add(MarketItemMock(name="item_2", price=5))
    shopping_cart = MyShoppingCart(
        db_session_mock, cart_class=CartMock, market_class=MarketItemMock
    )
    shopping_cart.add_item("item_2", 10)
    assert db_session_mock.query(CartMock).filter_by(name="item_2").first() == CartMock(
        name="item_2", price=5, quantity=10
    )


def test_remove_item():
    db_session_mock = UnifiedAlchemyMagicMock()
    db_session_mock.add(CartMock(name="item_3", price=50, quantity=10))
    shopping_cart = MyShoppingCart(
        db_session_mock, cart_class=CartMock, market_class=MarketItemMock
    )
    shopping_cart.remove_item(0)
    assert db_session_mock.query(CartMock).first() is None
