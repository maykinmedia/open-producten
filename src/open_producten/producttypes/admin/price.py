from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from ..models import Price, PriceOption


class PriceOptionInlineFormSet(BaseInlineFormSet):

    def clean(self):
        """Check that at least one option has been added."""
        super().clean()
        if any(self.errors):
            return
        if not any(
            cleaned_data and not cleaned_data.get("DELETE", False)
            for cleaned_data in self.cleaned_data
        ):
            raise ValidationError("At least one option required.")


class PriceOptionInline(admin.TabularInline):
    model = PriceOption
    extra = 1
    ordering = ("description",)
    formset = PriceOptionInlineFormSet


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    model = Price
    inlines = [PriceOptionInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")
