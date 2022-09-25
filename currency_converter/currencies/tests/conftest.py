import typing as tp

import pytest
from django.utils import timezone

from currency_converter.currencies.tests.factories import (
    CurrencyFactory,
    CurrencyRateFactory,
)


@pytest.fixture
def currency_generator() -> tp.Callable:
    def inner(*, symbol: str, open_rate: int, rate_number: int = 3):
        currency = CurrencyFactory(symbol=symbol)
        now = timezone.now().date()
        CurrencyRateFactory.create_batch(
            rate_number, source=currency, open=open_rate, date=now
        )
        return currency

    return inner
