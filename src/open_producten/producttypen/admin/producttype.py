from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext as _

from ..models import Onderwerp, ProductType
from .bestand import BestandInline
from .link import LinkInline
from .vraag import VraagInline


class ProductTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = "__all__"

    onderwerpen = forms.ModelMultipleChoiceField(
        label=_("onderwerpen"),
        queryset=Onderwerp.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_("Onderwerp"), is_stacked=False),
    )

    def clean(self):
        cleaned_data = super().clean()
        if len(cleaned_data["onderwerpen"]) == 0:
            self.add_error("onderwerpen", _("Er is minimaal één onderwerp vereist."))
        return cleaned_data


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("naam", "aanmaak_datum", "display_onderwerpen", "gepubliceerd")
    list_filter = ("gepubliceerd", "onderwerpen")
    list_editable = ("gepubliceerd",)
    date_hierarchy = "aanmaak_datum"
    autocomplete_fields = (
        # "organisations",
        # "contacts",
        # "locations",
    )
    search_fields = ("naam",)
    ordering = ("naam",)
    save_on_top = True
    form = ProductTypeAdminForm
    inlines = (BestandInline, LinkInline, VraagInline)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "onderwerpen",
                # "contacts", "locations", "organisations"
            )
        )

    @admin.display(description="onderwerpen")
    def display_onderwerpen(self, obj):
        return ", ".join(p.naam for p in obj.onderwerp.all())
