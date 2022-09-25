from unittest.mock import Mock, patch

import pytest

from currency_converter.currencies.models import Currency
from currency_converter.currencies.services import CurrencyService

pytestmark = pytest.mark.django_db


class TestServiceCurrency:
    def test_get_available_currencies_symbols(self, currency_generator):
        currency_generator(symbol="EUR", rate_number=0, open_rate=0.5)
        currency_generator(symbol="USD", rate_number=0, open_rate=0)

        symbols = CurrencyService.get_available_currencies_symbols()
        assert symbols == ["EUR", "USD"]

    def test_get_or_generate_currencies_no_exists(self, currency_generator):
        qs = CurrencyService.get_or_generate_currencies(currencies=["EUR", "USD"])
        assert list(qs.values_list("symbol", flat=True)) == ["EUR", "USD"]
        assert qs.count() == 2

    def test_get_or_generate_currencies_partly_exists(self, currency_generator):
        currency_generator(symbol="USD", rate_number=0, open_rate=0)
        qs = CurrencyService.get_or_generate_currencies(currencies=["EUR", "USD"])
        assert list(qs.values_list("symbol", flat=True)) == ["EUR", "USD"]
        assert qs.count() == 2

    def test_get_or_generate_currencies_fully_exists(self, currency_generator):
        currency_generator(symbol="EUR", rate_number=0, open_rate=0.5)
        currency_generator(symbol="USD", rate_number=0, open_rate=0)
        qs = CurrencyService.get_or_generate_currencies(currencies=["EUR", "USD"])
        assert list(qs.values_list("symbol", flat=True)) == ["EUR", "USD"]
        assert qs.count() == 2

    @pytest.mark.parametrize(
        "input_data,output_data",
        [
            [["EUR", "USD"], [("EUR", "USD"), ("USD", "EUR")]],
            [
                ["EUR", "USD", "PLN"],
                [
                    ("EUR", "USD"),
                    ("EUR", "PLN"),
                    ("USD", "EUR"),
                    ("USD", "PLN"),
                    ("PLN", "EUR"),
                    ("PLN", "USD"),
                ],
            ],
        ],
    )
    def test_get_currencies_permutations(self, input_data, output_data):
        result = CurrencyService.get_currencies_permutations(currencies=input_data)
        assert list(result) == output_data

    @patch("currency_converter.currencies.services.CurrencyRateService")
    @patch(
        "currency_converter.currencies.services.CurrencyService.get_currencies_permutations"
    )
    def test_load_currencies(
        self, mock_permutations, mocked_rate_service, currency_generator
    ):
        mock_permutations.return_value = [("USD", "EUR"), ("EUR", "USD")]
        period = "1mo"

        source = currency_generator(symbol="EUR", open_rate=1, rate_number=0)
        target = currency_generator(symbol="USD", open_rate=1, rate_number=0)

        mocked_rate_service.return_value.load_period = Mock()
        mocked_rate_service.return_value.load_period.return_value = (1, 2)

        CurrencyService.load_currencies(currencies=["EUR", "USD"], period=period)

        assert mocked_rate_service.call_count == 2
        mocked_rate_service.assert_called_with(
            source_currency=source, target_currency=target
        )

        assert mocked_rate_service.return_value.load_period.call_count == 2
        mocked_rate_service.return_value.load_period.assert_called_with(period="1mo")

    def test_clean_currencies(self, currency_generator):
        currency_generator(symbol="EUR", rate_number=1, open_rate=0.5)
        currency_generator(symbol="USD", rate_number=0, open_rate=0)

        qs = Currency.objects.all()
        assert qs.count() == 3
        CurrencyService.clean_currencies()
        assert qs.count() == 1
        assert qs.first().symbol == "EUR"
