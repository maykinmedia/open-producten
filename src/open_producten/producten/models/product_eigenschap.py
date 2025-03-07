from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.producten.models import Product
from open_producten.producttypen.models import Eigenschap
from open_producten.utils.models import BaseModel


class ProductEigenschap(BaseModel):

    waarde = models.CharField(
        verbose_name=_("waarde"),
        max_length=255,
        help_text=_("De waarde van de eigenschap."),
        validators=[RegexValidator(r"^[^:\[\]]+$")],
    )

    eigenschap = models.ForeignKey(
        Eigenschap,
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="waardes",
        help_text=_("Het eigenschap waarbij deze waarde hoort."),
    )

    product = models.ForeignKey(
        Product,
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="eigenschappen",
        help_text=_("Het product waarbij deze eigenschap hoort."),
    )

    @property
    def naam(self):
        return self.eigenschap.naam

    class Meta:
        verbose_name = _("product eigenschap")
        verbose_name_plural = _("product eigenschappen")
        unique_together = (("product", "eigenschap"),)

    def clean(self):
        validate_eigenschap_part_of_producttype(
            self.eigenschap, self.waarde, self.product
        )

    def __str__(self):
        return f"{self.eigenschap.naam} {self.waarde} {self.product.naam}"


def validate_eigenschap_part_of_producttype(eigenschap, waarde, product):
    if eigenschap.product_type != product.product_type:
        raise ValidationError(
            {
                "eigenschap": _(
                    "eigenschap {}: {} is niet onderdeel van het producttype {}"
                ).format(eigenschap.naam, waarde, product.product_type.naam)
            }
        )
