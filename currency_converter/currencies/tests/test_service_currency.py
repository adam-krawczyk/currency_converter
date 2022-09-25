from unittest.mock import Mock, patch

import pandas as pd
import pytest
from django.conf import settings

from currency_converter.currencies.services import CurrencyRateService

pytestmark = pytest.mark.django_db


class TestServiceRateCurrency:
    @patch(
        "currency_converter.currencies.services.CurrencyRateService._CurrencyRateService__update_or_create_rate"
    )
    @patch("yfinance.Ticker")
    @patch(
        "currency_converter.currencies.services.CurrencyRateService._CurrencyRateService__validate_period"
    )
    def test_load_period(
        self, mock_validate, mock_ticker, mock_update_rate, currency_generator
    ):
        source = currency_generator(symbol="EUR", rate_number=0, open_rate=0.5)
        target = currency_generator(symbol="USD", rate_number=0, open_rate=3)

        # mock function responses
        df = pd.read_csv(
            f"{settings.APPS_DIR}/currencies/tests/mock_data/currency-rate.csv",
            index_col="Date",
            parse_dates=True,
        )
        mock_ticker.return_value.history = Mock()
        mock_ticker.return_value.history.return_value = df
        mock_update_rate.return_value = True

        service = CurrencyRateService(source_currency=source, target_currency=target)
        service.load_period(period="1mo")

        # check is validated
        assert mock_validate.call_count == 1
        mock_validate.assert_called_with(period="1mo")

        # mock ticker and check is valid request executed
        assert mock_ticker.call_count == 1
        mock_ticker.assert_called_with(f"{source.symbol}{target.symbol}=X")

        # check is updated record in valid way
        assert mock_update_rate.call_count == 1
        mock_update_rate.assert_called_with(
            date=pd.Timestamp("2022-09-26 00:00:00"),
            open_rate=145.44000244140625,
            high_rate=146.27999877929688,
            low_rate=144.6999969482422,
            close_rate=146.25999450683594,
        )
