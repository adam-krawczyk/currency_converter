from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from currency_converter.currencies.api.views import (
    CurrencyExchangeView,
    CurrencyViewSet,
)

app_name = "api"

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("currency", CurrencyViewSet)


urlpatterns = router.urls + [
    path(
        "currency/<str:source>/<str:target>/",
        CurrencyExchangeView.as_view(),
        name="currency-exchange",
    )
]
