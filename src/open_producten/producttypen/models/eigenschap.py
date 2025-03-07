from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel


class Eigenschap(BaseModel):

    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("De naam van de eigenschap."),
        validators=[RegexValidator(r"^[^:\[\]]+$")],
    )

    product_type = models.ForeignKey(
        "ProductType",
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="eigenschappen",
        help_text=_("Het producttype waarbij deze eigenschap hoort."),
    )

    class Meta:
        verbose_name = _("eigenschap")
        verbose_name_plural = _("eigenschappen")
        unique_together = (("product_type", "naam"),)

    def __str__(self):
        return self.naam
