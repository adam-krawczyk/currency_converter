import datetime

from django.db.models import QuerySet
from django.utils import timezone


class CurrencySelector:
    @staticmethod
    def get_available_currencies() -> QuerySet:
        from currency_converter.currencies.models import Currency

        return Currency.objects.all()


class CurrencyRateSelector:
    @staticmethod
    def get_available_currency_rates() -> QuerySet:
        from currency_converter.currencies.models import CurrencyRate

        return CurrencyRate.objects.all()

    @staticmethod
    def get_available_currency_rates_from_date(date: datetime.date) -> QuerySet:
        return CurrencyRateSelector.get_available_currency_rates().filter(date__gt=date)

    @staticmethod
    def get_available_latest_currency_rates() -> QuerySet:
        rates_min_date = timezone.now() - datetime.timedelta(days=3)
        return CurrencyRateSelector.get_available_currency_rates_from_date(
            date=rates_min_date
        )
