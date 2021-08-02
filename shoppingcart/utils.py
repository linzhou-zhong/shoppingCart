from forex_python.converter import CurrencyRates
import logging

cache = {}


def get_currency_rate(currency_type: str) -> float:
    """
    Use CurrencyRates APi to get current currency rate
    :argument
        :param currency_type: Type of currency to be convert in
    :return: The rate of currency
    """
    if cache.get(currency_type) is None:
        logging.info("add {} currency rate into cache".format(currency_type))
        c = CurrencyRates()
        cache[currency_type] = float(c.get_rate("EUR", currency_type))

    return cache[currency_type]


def convert_currency(product_price: float, currency_type: str) -> float:
    """
    Calculate the converted total spending by provided currency type
    :argument
        :param product_price: The current total spending
        :param currency_type: The type of current to convert in
    :return: The total spending in different currency
    """
    return product_price * get_currency_rate(currency_type)
