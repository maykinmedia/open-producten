import datetime
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel

from .producttype import ProductType


class Prijs(BaseModel):
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("product type"),
        on_delete=models.CASCADE,
        related_name="prijzen",
        help_text=_("Het product type waarbij deze prijs hoort."),
    )
    actief_vanaf = models.DateField(
        verbose_name=_("start datum"),
        validators=[MinValueValidator(datetime.date.today)],
        help_text=_("De datum vanaf wanneer de prijs actief is."),
    )

    class Meta:
        verbose_name = _("Prijs")
        verbose_name_plural = _("Prijzen")
        unique_together = ("product_type", "actief_vanaf")

    def __str__(self):
        return f"{self.product_type.naam} {self.actief_vanaf}"


class PrijsOptie(BaseModel):
    prijs = models.ForeignKey(
        Prijs,
        verbose_name=_("prijs"),
        on_delete=models.CASCADE,
        related_name="prijsopties",
        help_text=_("De prijs waarbij deze optie hoort."),
    )
    bedrag = models.DecimalField(
        verbose_name=_("bedrag"),
        decimal_places=2,
        max_digits=8,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("Het bedrag van de prijs optie."),
    )
    beschrijving = models.CharField(
        verbose_name=_("beschrijving"),
        max_length=100,
        help_text=_("Korte beschrijving van de optie."),
    )

    class Meta:
        verbose_name = _("Prijs optie")
        verbose_name_plural = _("Prijs opties")

    def __str__(self):
        return f"{self.beschrijving} {self.bedrag}"
