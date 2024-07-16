from django.core.validators import MinLengthValidator, RegexValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.core.models import BaseModel
from open_producten.producttypes.models import ProductType

from .validators import validate_bsn


class Product(BaseModel):
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        on_delete=models.RESTRICT,
        help_text=_("The type of this product"),
        related_name="products",
    )

    start_date = models.DateField(
        _("Start date"), help_text=_("The start date for this product")
    )
    end_date = models.DateField(
        _("End date"), help_text=_("The end date for this product")
    )

    bsn = models.CharField(
        _("BSN"),
        help_text=_(
            "The BSN of the product owner. Bsn of 8 characters needs a leading 0."
        ),
        validators=[validate_bsn],
        null=True,
        blank=True,
    )

    kvk = models.CharField(
        _("KVK number"),
        help_text=_("The KVK number of the product owner"),
        max_length=8,
        validators=[MinLengthValidator(8), RegexValidator("^[0-9]*$")],
        null=True,
        blank=True,
    )

    @property
    def product_type_name(self):
        return self.product_type.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def clean(self):
        if not self.bsn and not self.kvk:
            raise ValidationError(
                "A product must be linked to a bsn or kvk number (or both)"
            )

        if self.id:
            self.validate_fields()

    def validate_fields(self):
        """Validates that all required fields are present and checks if all fields are part of product type."""
        filled_in_fields = self.data.only("field_id", "field__name").all()
        fields = self.product_type.fields.only("id", "name", "required").all()

        required_field_ids = [field.id for field in fields if field.required]

        for filled_field in filled_in_fields:
            if filled_field not in fields:
                raise ValidationError(
                    f"field {filled_field.name} is not part of {self.product_type.name}"
                )
            else:
                required_field_ids.remove(filled_field.id)

        if required_field_ids:
            raise ValidationError("Missing required fields.")

    def __str__(self):
        return f"{self.bsn if self.bsn else self.kvk} {self.product_type.name}"
