from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel

from .producttype import ProductType


class Field(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=255, help_text=_("The name of the field")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Short description of the field"),
        max_length=300,
    )

    class FieldTypes(models.TextChoices):
        """Formio field types used in Open Forms."""

        BSN = "bsn"
        CHECKBOX = "checkbox"
        COSIGN = "Cosign"
        CURRENCY = "currency"
        DATE = "date"
        DATETIME = "datetime"
        EMAIL = "email"
        FILE = "file"
        IBAN = "iban"
        LICENSE_PLATE = "licenseplate"
        MAP = "map"
        NUMBER = "number"
        PASSWORD = "password"
        PHONE_NUMBER = "phoneNumber"
        POSTCODE = "postcode"
        RADIO = "radio"
        SELECT = "select"
        SELECT_BOXES = "selectBoxes"
        SIGNATURE = "signature"
        TEXTFIELD = "textfield"
        TIME = "time"

    type = models.CharField(
        max_length=255,
        choices=FieldTypes.choices,
        default=FieldTypes.TEXTFIELD,
        verbose_name=_("Type"),
        help_text=_("The formio type of the field"),
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        verbose_name=_("Product Type"),
        help_text=_("The product type that this field is part of"),
        related_name="fields",
    )
    is_required = models.BooleanField(default=False)
    choices = ArrayField(
        models.CharField(max_length=100, blank=True),
        verbose_name=_("Choices"),
        default=list,
        blank=True,
        null=True,
        help_text=_("The Choices that can be selected in the form"),
    )

    choice_fields = (FieldTypes.RADIO, FieldTypes.SELECT, FieldTypes.SELECT_BOXES)

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")

    def clean(self):
        if self.type in self.choice_fields and not self.choices:
            raise ValidationError(f"Choices are required for {self.type}")

        if self.choices and self.type not in self.choice_fields:
            raise ValidationError(f"{self.type} cannot have choices")

    def __str__(self):
        return self.name
