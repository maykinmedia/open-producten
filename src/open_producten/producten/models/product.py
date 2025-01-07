from datetime import date

from django.core.validators import MinLengthValidator, RegexValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.logging.logevent import audit_automation_update
from open_producten.producttypen.models import ProductType
from open_producten.producttypen.models.producttype import ProductStateChoices
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
        help_text=_(
            "De start datum van dit product. Op deze datum zal de status van het product automatisch naar ACTIEF worden gezet. Op het moment dat de start_datum wordt ingevuld moet de status ACTIEF op het product type zijn toegestaan."
        ),
        null=True,
        blank=True,
    )
    eind_datum = models.DateField(
        _("eind datum"),
        help_text=_(
            "De einddatum van dit product. Op deze datum zal de status van het product automatisch naar VERLOPEN worden gezet. Op het moment dat de eind_datum wordt ingevuld moet de status VERLOPEN op het product type zijn toegestaan."
        ),
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

    status = models.CharField(
        _("status"),
        choices=ProductStateChoices.choices,
        help_text=_(
            "De status opties worden bepaald door het veld 'toegestane statussen' van het gerelateerde product type."
        ),
        default=ProductStateChoices.INITIEEL.value,
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

    @property
    def status_choices(self):
        """
        Returns all ProductStateChoices that are enabled on the product type.
        """
        choices = [
            (ProductStateChoices.INITIEEL.value, ProductStateChoices.INITIEEL.label)
        ]
        if not hasattr(self, "product_type"):
            return choices
        return choices + [
            choice
            for choice in ProductStateChoices.choices
            if choice[0] in self.product_type.toegestane_statussen
        ]

    def clean(self):
        validate_bsn_or_kvk(self.bsn, self.kvk)
        validate_status(self.status, self.product_type)
        validate_dates(self.start_datum, self.eind_datum, self.product_type)
        validate_verbruiksobject(self.verbruiksobject, self.product_type)

    def save(self, *args, **kwargs):
        self.handle_start_datum()
        self.handle_eind_datum()
        super().save(*args, **kwargs)

    def handle_start_datum(self):
        if (
            self.start_datum
            and self.start_datum <= date.today()
            and self.status
            in (ProductStateChoices.INITIEEL, ProductStateChoices.GEREED)
        ):
            audit_automation_update(
                self, _("Status gezet naar ACTIEF vanwege de start datum.")
            )
            self.status = ProductStateChoices.ACTIEF

    def handle_eind_datum(self):
        if (
            self.eind_datum
            and self.eind_datum <= date.today()
            and self.status
            in (
                ProductStateChoices.INITIEEL,
                ProductStateChoices.GEREED,
                ProductStateChoices.ACTIEF,
            )
        ):
            audit_automation_update(
                self, _("Status gezet naar VERLOPEN vanwege de eind datum.")
            )
            self.status = ProductStateChoices.VERLOPEN

    def __str__(self):
        return f"{self.bsn if self.bsn else self.kvk} {self.product_type.naam}"


def validate_bsn_or_kvk(bsn, kvk):
    if not bsn and not kvk:
        raise ValidationError(
            _("Een product moet een bsn, kvk nummer of beiden hebben.")
        )


def validate_status(status, product_type):
    if (
        status != ProductStateChoices.INITIEEL.value
        and status not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "status": _(
                    "Status '{}' is niet toegestaan voor het product type {}."
                ).format(
                    ProductStateChoices(status).label,
                    product_type.naam,
                )
            }
        )


def validate_dates(start_datum, eind_datum, product_type):
    if (start_datum == eind_datum) and start_datum is not None:
        raise ValidationError(
            {
                _(
                    "De start datum en eind_datum van een product mogen niet op dezelfde dag vallen."
                )
            }
        )

    if (
        start_datum
        and ProductStateChoices.ACTIEF.value not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "start_datum": _(
                    "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type."
                )
            }
        )

    if (
        eind_datum
        and ProductStateChoices.VERLOPEN.value not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "eind_datum": _(
                    "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het product type."
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
