from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.logging.logevent import audit_automation_update
from open_producten.producttypen.models import ProductType
from open_producten.producttypen.models.producttype import ProductStateChoices
from open_producten.utils.models import BasePublishableModel


class PrijsFrequentieChoices(models.TextChoices):

    EENMALIG = "eenmalig", _("Eenmalig")
    MAANDELIJKS = "maandelijks", _("Maandelijks")
    JAARLIJKS = "jaarlijks", _("Jaarlijks")


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

    status = models.CharField(
        _("status"),
        choices=ProductStateChoices.choices,
        help_text=_(
            "De status opties worden bepaald door het veld 'toegestane statussen' van het gerelateerde product type."
        ),
        default=ProductStateChoices.INITIEEL,
    )

    prijs = models.DecimalField(
        verbose_name=_("bedrag"),
        decimal_places=2,
        max_digits=8,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("De prijs van het product."),
    )

    frequentie = models.CharField(
        _("Prijs frequentie"),
        max_length=30,
        choices=PrijsFrequentieChoices.choices,
        help_text=_("De frequentie van betalingen."),
    )

    verbruiksobject = models.JSONField(
        _("verbruiksobject"),
        null=True,
        blank=True,
        help_text=_(
            "Verbruiksobject van dit product. Wordt gevalideerd met het `verbruiksobject_schema` uit het product type."
        ),
    )

    dataobject = models.JSONField(
        _("dataobject"),
        null=True,
        blank=True,
        help_text=_(
            "Dataobject van dit product. Wordt gevalideerd met het `dataobject_schema` uit het product type."
        ),
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Producten")

    def clean(self):
        validate_dates(self.start_datum, self.eind_datum)

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
        return f"{self.product_type.naam} instantie."


def validate_status(status, product_type):
    if (
        status != ProductStateChoices.INITIEEL
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


def validate_dates(start_datum, eind_datum):
    if start_datum and eind_datum and (start_datum >= eind_datum):
        raise ValidationError(
            _(
                "De eind datum van een product mag niet op een eerdere of dezelfde dag vallen als de start datum."
            )
        )


def validate_start_datum(start_datum, product_type):

    if (
        start_datum
        and ProductStateChoices.ACTIEF not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "start_datum": _(
                    "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type."
                )
            }
        )


def validate_eind_datum(eind_datum, product_type):
    if (
        eind_datum
        and ProductStateChoices.VERLOPEN not in product_type.toegestane_statussen
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


def validate_dataobject(dataobject, product_type):
    try:
        if dataobject is not None and product_type.dataobject_schema is not None:
            product_type.dataobject_schema.validate(dataobject)
    except ValidationError:
        raise ValidationError(
            {
                "dataobject": _(
                    "Het dataobject komt niet overeen met het schema gedefinieerd op het product type."
                )
            },
        )
