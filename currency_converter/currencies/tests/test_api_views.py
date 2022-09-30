import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from currency_converter.currencies.tests.factories import CurrencyRateFactory

pytestmark = pytest.mark.django_db


class TestAPICurrencies:
    list_url = reverse("api:currency-list")

    @pytest.mark.parametrize("action_name", ["post", "put", "patch", "delete"])
    def test_list_not_allowed_methods(self, action_name, api_client):
        action = getattr(api_client, action_name)
        response = action(self.list_url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_list(self, api_client, currency_generator):
        number_of_rates = 2
        source = currency_generator(
            symbol="EUR", open_rate=4, rate_number=number_of_rates
        )

        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == number_of_rates + 1

        source_result = next(
            result for result in results if result["symbol"] == source.symbol
        )
        assert len(source_result["rates"]) == number_of_rates
        results.index(source_result)

    @pytest.mark.parametrize(
        "ordering_type,first_symbol",
        [
            ["-symbol", "USD"],
            ["symbol", "EUR"],
        ],
    )
    def test_list_sort(
        self, ordering_type, first_symbol, api_client, currency_generator
    ):
        currency_generator(symbol="EUR", rate_number=0)
        currency_generator(symbol="USD", rate_number=0)

        response = api_client.get(self.list_url, {"ordering": ordering_type})
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == 2
        assert results[0]["symbol"] == first_symbol

    @pytest.mark.parametrize(
        "search,expected_count",
        [
            ["US", 1],
            ["EU", 1],
            ["", 2],
        ],
    )
    def test_list_search(self, search, expected_count, api_client, currency_generator):
        currency_generator(symbol="EUR", rate_number=0)
        currency_generator(symbol="USD", rate_number=0)

        response = api_client.get(self.list_url, {"search": search})
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == expected_count
        assert search in results[0]["symbol"]

    @pytest.mark.parametrize("action_name", ["post", "put", "patch", "delete"])
    def test_detail_not_allowed_methods(
        self, action_name, api_client, currency_generator
    ):
        action = getattr(api_client, action_name)

        eur = currency_generator(symbol="EUR", rate_number=0)
        usd = currency_generator(symbol="USD", rate_number=0)
        CurrencyRateFactory(source=eur, target=usd)

        url = reverse("api:currency-exchange", args=["EUR", "USD"])
        response = action(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize(
        "source_currency,target_currency,rate_date,expected_rate_id",
        [
            ["USD", "EUR", str(timezone.now().date()), "USD/EUR"],
            ["USD", "EUR", "2022-09-01", "USD/EUR/2022-09-01"],
            ["USD", "EUR", "2022-09-02", "USD/EUR/2022-09-02"],
            ["EUR", "USD", str(timezone.now().date()), "EUR/USD"],
            ["EUR", "USD", "2022-09-01", "EUR/USD/2022-09-01"],
            ["EUR", "USD", "2022-09-02", "EUR/USD/2022-09-02"],
        ],
    )
    def test_detail_found(
        self,
        source_currency,
        target_currency,
        rate_date,
        expected_rate_id,
        api_client,
        currency_generator,
    ):
        eur = currency_generator(symbol="EUR", rate_number=0)
        usd = currency_generator(symbol="USD", rate_number=0)

        rates = {
            "EUR/USD": CurrencyRateFactory(
                source=eur, target=usd, date=str(timezone.now().date())
            ),
            "EUR/USD/2022-09-01": CurrencyRateFactory(
                source=eur, target=usd, date="2022-09-01"
            ),
            "EUR/USD/2022-09-02": CurrencyRateFactory(
                source=eur, target=usd, date="2022-09-02"
            ),
            "USD/EUR": CurrencyRateFactory(
                source=usd, target=eur, date=str(timezone.now().date())
            ),
            "USD/EUR/2022-09-01": CurrencyRateFactory(
                source=usd, target=eur, date="2022-09-01"
            ),
            "USD/EUR/2022-09-02": CurrencyRateFactory(
                source=usd, target=eur, date="2022-09-02"
            ),
        }

        url = reverse("api:currency-exchange", args=[source_currency, target_currency])

        response = api_client.get(url, {"rate_date": rate_date})
        assert response.status_code == status.HTTP_200_OK

        expected_rate = rates[expected_rate_id]
        assert response.data["date"] == str(rate_date)
        assert response.data["open"] == str(expected_rate.open)
        assert response.data["high"] == str(expected_rate.high)
        assert response.data["low"] == str(expected_rate.low)
        assert response.data["close"] == str(expected_rate.close)

    @pytest.mark.parametrize(
        "source_currency,target_currency,rate_date",
        [
            ["USD", "EUR", "2022-09-01"],
            ["USD", "EUR", "2022-09-02"],
            ["EUR", "USD", "2022-09-02"],
            ["USD", "ISK", "2022-09-01"],
            ["ISK", "USD", "2022-09-01"],
        ],
    )
    def test_detail_not_found(
        self,
        source_currency,
        target_currency,
        rate_date,
        api_client,
        currency_generator,
    ):
        eur = currency_generator(symbol="EUR", rate_number=0)
        usd = currency_generator(symbol="USD", rate_number=0)
        CurrencyRateFactory(source=eur, target=usd, date="2022-09-01")

        url = reverse("api:currency-exchange", args=[source_currency, target_currency])

        response = api_client.get(url, {"rate_date": rate_date})

        assert response.status_code == status.HTTP_404_NOT_FOUND
