from rest_framework import serializers

from currency_converter.currencies.models import Currency, CurrencyRate
from currency_converter.currencies.validators import validate_currency_symbol


class CurrencyRateShortSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="target.symbol")
    rate_date = serializers.DateField(source="date")

    class Meta:
        model = CurrencyRate
        fields = ("rate_date", "symbol")


class CurrencyExchangeViewSerializer(serializers.Serializer):
    source = serializers.CharField(validators=(validate_currency_symbol,))
    target = serializers.CharField(validators=(validate_currency_symbol,))
    rate_date = serializers.ListField(
        child=serializers.DateField(), max_length=1, required=False
    )


class CurrencySerializer(serializers.ModelSerializer):
    rates = CurrencyRateShortSerializer(many=True)

    class Meta:
        model = Currency
        fields = ("symbol", "rates")


class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = (
            "date",
            "open",
            "high",
            "low",
            "close",
        )
