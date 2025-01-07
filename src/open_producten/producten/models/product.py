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
        _("start datum"),
        help_text=_("De start datum van dit product."),
        null=True,
        blank=True,
    )
    eind_datum = models.DateField(
        _("eind datum"),
        help_text=_("De einddatum van dit product."),
        null=True,
        blank=True,
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

    verbruiksobject = models.JSONField(
        _("verbruiksobject"),
        null=True,
        blank=True,
        help_text=_(
            "Verbruiksobject van dit product. Wordt gevalideerd met het `verbruiksobject_schema` uit het product type."
        ),
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Producten")

    def clean(self):
        validate_bsn_or_kvk(self.bsn, self.kvk)
        validate_dates(self.start_datum, self.eind_datum)
        validate_verbruiksobject(self.verbruiksobject, self.product_type)

    def __str__(self):
        return f"{self.bsn if self.bsn else self.kvk} {self.product_type.naam}"


def validate_bsn_or_kvk(bsn, kvk):
    if not bsn and not kvk:
        raise ValidationError(
            _("Een product moet een bsn, kvk nummer of beiden hebben.")
        )


def validate_dates(start_datum, eind_datum):
    if (start_datum == eind_datum) and start_datum is not None:
        raise ValidationError(
            {
                _(
                    "De start datum en eind_datum van een product mogen niet op dezelfde dag vallen."
                )
            }
        )

def validate_verbruiksobject(verbruiksobject, product_type):
    try:
        if (
            verbruiksobject is not None
            and product_type.verbruiksobject_schema is not None
        ):
            product_type.verbruiksobject_schema.validate(verbruiksobject)
    except ValidationError:
        raise ValidationError(
            {
                "verbruiksobject": _(
                    "Het verbruiksobject komt niet overeen met het schema gedefinieerd op het product type."
                )
            },
        )
