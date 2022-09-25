from django.db.models import Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from currency_converter.currencies.api.serializers import (
    CurrencyExchangeViewSerializer,
    CurrencyRateSerializer,
    CurrencySerializer,
)
from currency_converter.currencies.selectors import (
    CurrencyRateSelector,
    CurrencySelector,
)


class CurrencyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CurrencySelector.get_available_currencies().prefetch_related(
        Prefetch(
            "rates",
            CurrencyRateSelector.get_available_latest_currency_rates().select_related(
                "target"
            ),
        )
    )
    serializer_class = CurrencySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("symbol",)
    ordering_fields = ("symbol",)


class CurrencyExchangeView(GenericAPIView):
    queryset = CurrencyRateSelector.get_available_currency_rates()
    serializer_class = CurrencyRateSerializer

    def get_rates(self, data):
        qs = (
            super()
            .get_queryset()
            .filter(source__symbol=data["source"], target__symbol=data["target"])
        )
        if rate_date := data.get("rate_date"):
            qs = qs.filter(date=rate_date[0])
        return qs

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="rate_date",
                description="Filter by rate date",
                required=False,
                type=OpenApiTypes.DATE,
            ),
        ]
    )
    def get(self, request, source: str, target: str):
        serializer = CurrencyExchangeViewSerializer(
            data={**request.query_params, "source": source, "target": target}
        )
        serializer.is_valid(raise_exception=True)

        rate = self.get_rates(data=serializer.data).first()
        if not rate:
            raise NotFound
        serializer = self.get_serializer(rate)
        return Response(serializer.data)
