import logging

from config.celery_app import app

logger = logging.getLogger(__name__)


@app.task
def load_currency_rate(source: str, target: str, period: str):
    from currency_converter.currencies.models import Currency
    from currency_converter.currencies.services import CurrencyRateService

    try:
        source_obj = Currency.objects.get(symbol=source)
        target_obj = Currency.objects.get(symbol=target)
    except Currency.DoesNotExist:
        logger.error(f"One of currencies does not exist: {source} / {target}")
        return

    service = CurrencyRateService(
        source_currency=source_obj, target_currency=target_obj
    )
    return service.load_period(period=period)


@app.task
def load_currency_rates():
    from currency_converter.currencies.services import CurrencyService

    service = CurrencyService()
    symbols = service.get_available_currencies_symbols()
    permutations = CurrencyService.get_currencies_permutations(currencies=symbols)

    for source, target in permutations:
        load_currency_rate.delay(source=source, target=target, period="1d")
