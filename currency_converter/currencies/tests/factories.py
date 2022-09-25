import datetime
import string

import factory.fuzzy
from factory.django import DjangoModelFactory

from currency_converter.currencies.models import Currency, CurrencyRate


class CurrencyFactory(DjangoModelFactory):

    symbol = factory.Sequence(lambda n: f"{string.ascii_uppercase[n:3]}")

    class Meta:
        model = Currency


class CurrencyRateFactory(DjangoModelFactory):
    source = factory.SubFactory(CurrencyFactory)
    target = factory.SubFactory(CurrencyFactory)
    date = factory.fuzzy.FuzzyDate(
        datetime.date(2022, 9, 1), datetime.date(2022, 9, 30)
    )
    open = factory.fuzzy.FuzzyDecimal(0.3, 233.2, 10)
    high = factory.fuzzy.FuzzyDecimal(0.3, 233.2, 10)
    low = factory.fuzzy.FuzzyDecimal(0.3, 233.2, 10)
    close = factory.fuzzy.FuzzyDecimal(0.3, 233.2, 10)

    class Meta:
        model = CurrencyRate
