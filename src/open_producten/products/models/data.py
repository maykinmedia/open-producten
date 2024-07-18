from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.producttypes.models import Field, FieldTypes
from open_producten.utils.validators import validate_postal_code

from .product import Product
from .validators import (
    validate_bsn,
    validate_checkbox,
    validate_datetime_format,
    validate_radio,
    validate_regex,
    validate_select,
    validate_select_boxes,
)


class Data(models.Model):
    field = models.ForeignKey(
        Field,
        verbose_name=_("Field"),
        on_delete=models.CASCADE,
        help_text=_("The field that this data belongs to"),
        related_name="data",
    )
    data = models.CharField(_("Data"), help_text=_("The value of the field"))

    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.RESTRICT,
        help_text=_("The product that this data belongs to"),
        related_name="data",
    )

    class Meta:
        verbose_name = _("Data")
        verbose_name_plural = _("Data")

    def __str__(self):
        return f"{self.field.name} {self.product_type.name}"

    @property
    def product_type(self):
        return self.field.product_type

    formatters = {
        FieldTypes.NUMBER: float,
        FieldTypes.CHECKBOX: lambda data: data.lower() == "true",
        FieldTypes.DATE: lambda data: datetime.strptime(data, "%Y-%m-%d").date(),
        FieldTypes.DATETIME: lambda data: datetime.strptime(
            data, "%Y-%m-%dT%H:%M:%S%z"
        ),
        FieldTypes.TIME: lambda data: datetime.strptime(data, "%H:%M:%S").time(),
        FieldTypes.MAP: lambda data: data.split(","),
        FieldTypes.SELECT: lambda data: data.split(","),
    }

    cleaners = {
        FieldTypes.BSN: lambda data: validate_bsn(data),
        FieldTypes.CHECKBOX: lambda data: validate_checkbox(data),
        FieldTypes.COSIGN: lambda data: validate_regex(
            data, r"^.+@.+\..+$", FieldTypes.EMAIL
        ),
        FieldTypes.CURRENCY: lambda data: validate_regex(
            data, r"^\d+,?\d{0,2}$", FieldTypes.CURRENCY
        ),
        FieldTypes.DATE: lambda data: validate_datetime_format(
            data, "%Y-%m-%d", FieldTypes.DATE
        ),
        FieldTypes.DATETIME: lambda data: validate_datetime_format(
            data, "%Y-%m-%dT%H:%M:%S%z", FieldTypes.DATETIME
        ),
        FieldTypes.EMAIL: lambda data: validate_regex(
            data, r"^.+@.+\..+$", FieldTypes.EMAIL
        ),
        FieldTypes.FILE: lambda data: None,  # TODO
        FieldTypes.IBAN: lambda data: None,  # TODO
        FieldTypes.LICENSE_PLATE: lambda data: None,  # TODO
        FieldTypes.MAP: lambda data: validate_regex(
            data, r"^\d+\.?\d*,\d+\.?\d*$", FieldTypes.MAP
        ),
        FieldTypes.NUMBER: lambda data: validate_regex(
            data, r"^\d+\.?\d*$", FieldTypes.NUMBER
        ),
        # FieldTypes.PASSWORD STR
        FieldTypes.PHONE_NUMBER: lambda data: None,  # TODO
        FieldTypes.POSTCODE: lambda data: validate_postal_code(data),
        FieldTypes.SIGNATURE: lambda data: validate_regex(
            data, r"^data:image/png;base64,.*$", FieldTypes.SIGNATURE
        ),
        # FieldTypes.TEXTFIELD STR
        FieldTypes.TIME: lambda data: validate_datetime_format(
            data, "%H:%M:%S", FieldTypes.TIME
        ),
    }

    choice_cleaners = {
        FieldTypes.RADIO: lambda data, choices: validate_radio(data, choices),
        FieldTypes.SELECT: lambda data, choices: validate_select(data, choices),
        FieldTypes.SELECT_BOXES: lambda data, choices: validate_select_boxes(
            data, choices
        ),
    }

    def format(self):
        if self.field.type in self.formatters:
            return self.formatters[self.field.type](self.data)

    def clean(self):
        if self.field.type in self.cleaners:
            self.cleaners[self.field.type](self.data)

        elif self.field.type in self.choice_cleaners:
            self.choice_cleaners[self.field.type](self.data, self.field.choices)
