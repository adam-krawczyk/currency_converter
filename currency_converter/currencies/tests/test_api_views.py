import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAPICurrencies:
    list_url = reverse("api:currency-list")
    leave_group_url = reverse("api:currency-exchange", args=["EUR", "PLN"])

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
        currency_generator(symbol="EUR", rate_number=0, open_rate=0.5)
        currency_generator(symbol="USD", rate_number=0, open_rate=0)

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
        currency_generator(symbol="EUR", rate_number=0, open_rate=0.5)
        currency_generator(symbol="USD", rate_number=0, open_rate=0)

        response = api_client.get(self.list_url, {"search": search})
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == expected_count
        assert search in results[0]["symbol"]
