from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.django_db


class TestCurrenciesTasks:
    @patch(
        "currency_converter.currencies.services.CurrencyService.get_available_currencies_symbols"
    )
    @patch("currency_converter.currencies.tasks.load_currency_rate.delay")
    def test_load_currency_rates(
        self, mocked_load_currency_rate, mocked_get_available_currencies_symbols
    ):
        from currency_converter.currencies.tasks import load_currency_rates

        mocked_get_available_currencies_symbols.return_value = ["EUR", "USD"]

        load_currency_rates()
        assert mocked_load_currency_rate.call_count == 2
        mocked_load_currency_rate.assert_called_with(
            source="USD", target="EUR", period="1d"
        )

    @patch("currency_converter.currencies.services.CurrencyRateService")
    def test_load_currency_rate(self, mocked_rate_service, currency_generator):
        from currency_converter.currencies.tasks import load_currency_rate

        source = currency_generator(symbol="EUR", open_rate=1, rate_number=0)
        target = currency_generator(symbol="PLN", open_rate=1, rate_number=0)
        mocked_rate_service.return_value.load_period = Mock()

        load_currency_rate(source=source.symbol, target=target.symbol, period="1mo")

        assert mocked_rate_service.call_count == 1
        mocked_rate_service.assert_called_with(
            source_currency=source, target_currency=target
        )

        assert mocked_rate_service.return_value.load_period.call_count == 1
        mocked_rate_service.return_value.load_period.assert_called_with(period="1mo")
