import datetime
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .producttype import ProductType


class Price(models.Model):
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        on_delete=models.CASCADE,
        related_name="prices",
        help_text=_("The product type that this price belongs to"),
    )
    start_date = models.DateField(
        verbose_name=_("Start date"),
        validators=[MinValueValidator(datetime.date.today)],
        help_text=_("The start date for this price"),
    )

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = ("product_type", "start_date")

    def __str__(self):
        return self.product_type.name, self.start_date


class PriceOption(models.Model):
    price = models.ForeignKey(
        Price,
        verbose_name=_("Price"),
        on_delete=models.CASCADE,
        related_name="options",
        help_text=_("The price this option belongs to"),
    )
    cost = models.DecimalField(
        verbose_name=_("Cost"),
        decimal_places=2,
        max_digits=8,
        default=0,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("The cost of the price option"),
    )
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=100,
        help_text=_("Short description of the option"),
    )

    class Meta:
        verbose_name = _("Price option")
        verbose_name_plural = _("Price options")

    def __str__(self):
        return self.description
