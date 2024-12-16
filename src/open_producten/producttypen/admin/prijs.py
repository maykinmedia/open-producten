from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from ..models import Prijs, PrijsOptie


class PrijsOptieInlineFormSet(BaseInlineFormSet):

    def clean(self):
        """Check that at least one optie has been added."""
        super().clean()
        if any(self.errors):
            return
        if not any(
            cleaned_data and not cleaned_data.get("DELETE", False)
            for cleaned_data in self.cleaned_data
        ):
            raise ValidationError(_("Er is minimaal één optie vereist."))


class PrijsOptieInline(admin.TabularInline):
    model = PrijsOptie
    extra = 1
    ordering = ("beschrijving",)
    formset = PrijsOptieInlineFormSet


@admin.register(Prijs)
class PrijsAdmin(admin.ModelAdmin):
    model = Prijs
    inlines = [PrijsOptieInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")
