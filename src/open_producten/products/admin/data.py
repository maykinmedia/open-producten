from django.contrib import admin
from django.core.validators import ValidationError
from django.forms import BaseInlineFormSet

from open_producten.producttypes.models import ProductType

from ..models import Data


class DataInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        if not self.data:
            return

        product_type = ProductType.objects.get(pk=self.data["product_type"])
        required_fields = list(product_type.fields.filter(is_required=True).all())

        for form in self.forms:

            # empty form
            if not form.cleaned_data:
                continue

            field = form.cleaned_data["field"]

            if field.product_type != product_type:
                raise ValidationError(
                    f"field {field.name} is not part of {product_type.name}"
                )

            elif field in required_fields and not form.cleaned_data["DELETE"]:
                required_fields.remove(field)

        if required_fields:
            raise ValidationError("Missing required fields.")


class DataInline(admin.TabularInline):
    model = Data
    extra = 1
    formset = DataInlineFormSet
