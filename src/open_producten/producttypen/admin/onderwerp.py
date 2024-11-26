from django import forms
from django.contrib import admin
from django.forms import BaseModelFormSet
from django.utils.translation import gettext as _

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from ..models import Onderwerp, OnderwerpProductType
from .vraag import VraagInline


class ProductTypeInline(admin.TabularInline):
    model = OnderwerpProductType
    fields = ("product_type",)
    extra = 1


class OnderwerpAdminForm(movenodeform_factory(Onderwerp)):
    class Meta:
        model = Onderwerp
        fields = "__all__"


class OnderwerpAdminFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        data = {
            form.cleaned_data["id"]: form.cleaned_data["gepubliceerd"]
            for form in self.forms
        }

        for onderwerp, gepubliceerd in data.items():
            if children := onderwerp.get_children():
                if not gepubliceerd and any([data[child] for child in children]):
                    raise forms.ValidationError(
                        _(
                            "Hoofd onderwerpen moeten gepubliceerd zijn met gepubliceerde sub onderwerpen."
                        )
                    )


@admin.register(Onderwerp)
class OnderwerpAdmin(TreeAdmin):
    form = OnderwerpAdminForm
    inlines = (
        ProductTypeInline,
        VraagInline,
    )
    search_fields = ("naam",)
    list_display = (
        "naam",
        "gepubliceerd",
    )
    list_editable = ("gepubliceerd",)
    exclude = ("path", "depth", "numchild")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "naam",
                    "beschrijving",
                    "gepubliceerd",
                    "_position",
                    "_ref_node_id",
                ),
            },
        ),
    )

    list_filter = [
        "gepubliceerd",
    ]

    def get_changelist_formset(self, request, **kwargs):
        kwargs["formset"] = OnderwerpAdminFormSet
        return super().get_changelist_formset(request, **kwargs)
