from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce import models as tinymce_models

from open_producten.utils.models import BaseModel

from .producttype import ProductType


class FieldTypes(models.TextChoices):
    """Formio field types used in Open Forms."""

    BSN = "bsn"  # STR
    CHECKBOX = "checkbox"  # BOOL
    COSIGN = "Cosign"  # STR
    CURRENCY = "currency"  # STR
    DATE = "date"  # DATE
    DATETIME = "datetime"  # DATETIME
    EMAIL = "email"  # STR
    IBAN = "iban"  # STR
    LICENSE_PLATE = "licenseplate"  # STR
    MAP = "map"  # STR (remove brackets)
    NUMBER = "number"  # INT
    PASSWORD = "password"  # STR
    PHONE_NUMBER = "phoneNumber"  # STR
    POSTCODE = "postcode"  # STR
    RADIO = "radio"  # STR
    SELECT = "select"  # STR (remove brackets)
    SELECT_BOXES = "selectBoxes"  # STR
    SIGNATURE = "signature"  # STR
    TEXTFIELD = "textfield"  # STR
    TIME = "time"  # TIME


class Field(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=255, help_text=_("The name of the field")
    )
    description = tinymce_models.HTMLField(
        verbose_name=_("Description"),
        help_text=_("Short description of the field"),
        max_length=300,
    )

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
            raise ValidationError({"choices": f"Choices are required for {self.type}"})

        if self.choices and self.type not in self.choice_fields:
            raise ValidationError({"choices": f"{self.type} cannot have choices"})

    def __str__(self):
        return self.name
