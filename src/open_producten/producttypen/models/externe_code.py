from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel


class ExterneCode(BaseModel):

    systeem = models.CharField(
        verbose_name=_("systeem"),
        max_length=255,
        help_text=_("De systeem van de externe product code"),
    )

    code = models.CharField(
        verbose_name=_("code"),
        max_length=255,
        help_text=_("De code van de van het product type in het systeem"),
    )

    product_type = models.ForeignKey(
        "ProductType",
        verbose_name=_("product type"),
        on_delete=models.CASCADE,
        related_name="externe_codes",
        help_text=_("Het product type waarbij deze externe code hoort."),
    )

    class Meta:
        verbose_name = _("externe product type code")
        verbose_name_plural = _("externe product type codes")
        unique_together = (("product_type", "systeem"),)
