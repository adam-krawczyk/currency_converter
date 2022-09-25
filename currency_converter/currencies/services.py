import datetime
import itertools
import logging
import typing as tp
from decimal import Decimal

import yfinance as yf
from django.core.exceptions import ValidationError
from django.db.models import Count, QuerySet

from currency_converter.currencies import models as currencies_models
from currency_converter.currencies.models import Currency, CurrencyRate
from currency_converter.currencies.selectors import CurrencySelector

logger = logging.getLogger(__name__)


class CurrencyService:
    @staticmethod
    def get_available_currencies_symbols() -> tp.List[str]:
        return CurrencySelector.get_available_currencies().values_list(
            "symbol", flat=True
        )

    @staticmethod
    def get_or_generate_currencies(currencies: tp.List[str]) -> QuerySet:
        qs = CurrencySelector.get_available_currencies()
        missed_currencies = set(currencies) - set(qs.values_list("symbol", flat=True))
        if missed_currencies:
            objects = [
                Currency(symbol=currency.upper()) for currency in missed_currencies
            ]
            Currency.objects.bulk_create(objects)
        return qs.all()

    @staticmethod
    def get_currencies_permutations(*, currencies: tp.List[str]):
        return itertools.permutations(currencies, 2)

    @staticmethod
    def load_currencies(*, currencies: tp.List[str], period: str):
        total_created, total_updated = 0, 0
        permutations = CurrencyService.get_currencies_permutations(
            currencies=currencies
        )

        for source, target in permutations:
            service = CurrencyRateService(
                source_currency=source, target_currency=target
            )
            created, updated = service.load_period(period=period)
            total_created += created
            total_updated += updated

        return total_created, total_updated

    @staticmethod
    def clean_currencies() -> tp.Dict:
        return (
            Currency.objects.annotate(rate_count=Count("rates"))
            .filter(rate_count=0)
            .delete()
        )


class CurrencyRateService:
    def __init__(
        self,
        *,
        source_currency: "currencies_models.Currency",
        target_currency: "currencies_models.Currency",
    ):
        self.source_currency = source_currency
        self.target_currency = target_currency

    def __validate_period(self, *, period: str) -> bool:
        return period in self.get_available_periods()

    @staticmethod
    def get_available_periods() -> tp.List[str]:
        return ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    def __update_or_create_rate(
        self,
        *,
        date: datetime.datetime,
        open_rate: Decimal,
        high_rate: Decimal,
        low_rate: Decimal,
        close_rate: Decimal,
    ) -> bool:
        _, created = CurrencyRate.objects.update_or_create(
            source=self.source_currency,
            target=self.target_currency,
            date=date.date(),
            defaults={
                "open": open_rate,
                "high": high_rate,
                "low": low_rate,
                "close": close_rate,
            },
        )
        return created

    def __update_rates(self, *, period: str) -> tp.Tuple[int, int]:
        msft = yf.Ticker(f"{self.source_currency}{self.target_currency}=X")
        hist = msft.history(period=period)
        created, updated = 0, 0

        for date, record in zip(
            hist.index, hist[["Open", "High", "Low", "Close"]].values
        ):
            open_rate, high_rate, low_rate, close_rate = record
            if self.__update_or_create_rate(
                date=date,
                open_rate=open_rate,
                high_rate=high_rate,
                low_rate=low_rate,
                close_rate=close_rate,
            ):
                created += 1
            else:
                updated += 1

        if not created and not updated:
            msg = f"Record not found for currency {self.source_currency} -> {self.target_currency}"
            logger.warning(msg)
        else:
            msg = f"Currency {self.source_currency} -> {self.target_currency} updated {updated}, created {created}"
            logger.info(msg)
        return created, updated

    def load_period(self, *, period: str) -> tp.Tuple[int, int]:
        if not self.__validate_period(period=period):
            available = ", ".join(self.get_available_periods())
            raise ValidationError(f"Period option is invalid. Available: {available}")

        return self.__update_rates(period=period)
