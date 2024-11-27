from django.core.validators import MinLengthValidator, RegexValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.producttypen.models import ProductType
from open_producten.utils.models import BasePublishableModel

from .validators import validate_bsn


class Product(BasePublishableModel):
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        on_delete=models.RESTRICT,
        help_text=_("Het type van dit product"),
        related_name="producten",
    )

    start_datum = models.DateField(
        _("start datum"), help_text=_("De start datum van dit product.")
    )
    eind_datum = models.DateField(
        _("eind datum"), help_text=_("De einddatum van dit product.")
    )

    bsn = models.CharField(
        _("BSN"),
        help_text=_(
            "De BSN van de product eigenaar, BSN van 8 karakters moet met een extra 0 beginnen."
        ),
        validators=[validate_bsn],
        null=True,
        blank=True,
    )

    kvk = models.CharField(
        _("KVK nummer"),
        help_text=_("Het kvk nummer van de product eigenaar"),
        max_length=8,
        validators=[MinLengthValidator(8), RegexValidator("^[0-9]*$")],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Producten")

    def clean(self):
        if not self.bsn and not self.kvk:
            raise ValidationError(
                "Een product moet een bsn, kvk nummer of beiden hebben."
            )

    def __str__(self):
        return f"{self.bsn if self.bsn else self.kvk} {self.product_type.naam}"
