from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel


class Eigenschap(BaseModel):

    key = models.CharField(
        verbose_name=_("key"),
        max_length=255,
        help_text=_("De sleutel van de eigenschap"),
    )

    waarde = models.CharField(
        verbose_name=_("waarde"),
        max_length=255,
        help_text=_("De waarde van de eigenschap"),
    )

    product_type = models.ForeignKey(
        "ProductType",
        verbose_name=_("product type"),
        on_delete=models.CASCADE,
        related_name="eigenschappen",
        help_text=_("Het product type waarbij deze eigenschap hoort."),
    )

    class Meta:
        verbose_name = _("eigenschap")
        verbose_name_plural = _("eigenschappen")
        unique_together = (("product_type", "key"),)
