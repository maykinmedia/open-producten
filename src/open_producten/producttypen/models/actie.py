from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.producttypen.models import ProductType
from open_producten.producttypen.models.dmn_config import DmnConfig
from open_producten.utils.models import BaseModel


class Actie(BaseModel):
    beschrijving = models.CharField(
        verbose_name=_("beschrijving"),
        max_length=255,
        help_text=_("Korte beschrijving van de actie."),
    )

    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Producttype"),
        on_delete=models.RESTRICT,
        help_text=_("Het producttype waarbij deze actie hoort."),
        related_name="acties",
    )
    dmn_config = models.ForeignKey(
        DmnConfig,
        verbose_name=_("dmn config"),
        on_delete=models.CASCADE,
        related_name="prijsregels",
        help_text=_("de dmn engine waar de tabel is gedefinieerd."),
    )

    dmn_tabel_id = models.CharField(
        verbose_name=_("dmn tabel id"),
        max_length=255,
        help_text=_("id van de dmn tabel binnen de dmn instantie."),
    )
