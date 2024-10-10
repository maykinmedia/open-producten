from django import forms
from django.contrib import admin
from django.core.validators import ValidationError
from django.forms import BaseInlineFormSet, ModelForm

from open_producten.producttypes.models import Field, ProductType

from ..models import Data


class DataFieldSelect(forms.Select):
    """Select widget that adds the product type id to the option tag."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex=None, attrs=None
        )

        if option["value"]:
            option["attrs"]["product_type"] = str(
                Field.objects.get(pk=str(option["value"])).product_type_id
            )
        return option


class DataForm(ModelForm):
    class Meta:
        model = Data
        fields = "__all__"
        widgets = {"field": DataFieldSelect}


class DataInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form = DataForm

    def clean(self):
        super().clean()

        if not self.data:
            return

        product_type = ProductType.objects.get(pk=self.data["product_type"])
        required_fields = list(product_type.fields.filter(is_required=True))

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
            raise ValidationError(
                f"Missing required fields: {', '.join([str(field) for field in required_fields])}."
            )


class DataInline(admin.TabularInline):
    model = Data
    extra = 1
    formset = DataInlineFormSet
