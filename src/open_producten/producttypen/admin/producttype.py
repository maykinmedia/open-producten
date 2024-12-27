from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext as _

from ..models import ProductType, Thema
from .bestand import BestandInline
from .link import LinkInline
from .vraag import VraagInline


class ProductTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = "__all__"

    themas = forms.ModelMultipleChoiceField(
        label=_("thema's"),
        queryset=Thema.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_("Thema"), is_stacked=False),
    )

    def clean(self):
        cleaned_data = super().clean()
        if len(cleaned_data["themas"]) == 0:
            self.add_error("themas", _("Er is minimaal één thema vereist."))
        return cleaned_data


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = (
        "naam",
        "uniforme_product_naam",
        "aanmaak_datum",
        "display_themas",
        "gepubliceerd",
        "keywords",
    )
    list_filter = ("gepubliceerd", "themas")
    list_editable = ("gepubliceerd",)
    date_hierarchy = "aanmaak_datum"
    autocomplete_fields = (
        # "organisations",
        # "contacts",
        # "locations",
    )
    search_fields = ("naam", "uniforme_product_naam__naam", "keywords")
    ordering = ("naam",)
    save_on_top = True
    form = ProductTypeAdminForm
    inlines = (BestandInline, LinkInline, VraagInline)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "themas",
                # "contacts", "locations", "organisations"
            )
        )

    @admin.display(description="thema's")
    def display_themas(self, obj):
        return ", ".join(p.naam for p in obj.themas.all())
