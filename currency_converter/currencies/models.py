from django.db import models
from django.utils.translation import gettext_lazy as _

from currency_converter.currencies.validators import validate_currency_symbol


class Currency(models.Model):
    symbol = models.CharField(
        _("Symbol"), max_length=3, unique=True, validators=[validate_currency_symbol]
    )

    def __str__(self):
        return f"{self.symbol}"

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")


class CurrencyRate(models.Model):
    source = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        verbose_name=_("Source currency"),
        related_name="rates",
    )
    target = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        verbose_name=_("Target currency"),
        related_name="+",
    )
    date = models.DateField(_("Date"))
    open = models.DecimalField(_("Open rate"), max_digits=17, decimal_places=10)
    high = models.DecimalField(_("High rate"), max_digits=17, decimal_places=10)
    low = models.DecimalField(_("Low rate"), max_digits=17, decimal_places=10)
    close = models.DecimalField(_("Close rate"), max_digits=17, decimal_places=10)

    def __str__(self):
        return f"{self.source}->{self.target} {self.date}"

    class Meta:
        verbose_name = _("Currency rate")
        verbose_name_plural = _("Currencies rate")
        ordering = ("-date",)
