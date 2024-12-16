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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        gepubliceerd = cleaned_data["gepubliceerd"]
        ref_node = cleaned_data["_ref_node_id"]
        position = cleaned_data["_position"]

        if not ref_node:
            hoofd_onderwerp = None
        elif position == "sorted-child":
            hoofd_onderwerp = Onderwerp.objects.get(id=ref_node)
        else:  # sorted-sibling
            hoofd_onderwerp = Onderwerp.objects.get(id=ref_node).hoofd_onderwerp

        self.instance.clean_gepubliceerd_and_hoofd_onderwerp(
            gepubliceerd, hoofd_onderwerp
        )


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
                            "Sub-onderwerpen kunnen niet zijn gepubliceerd als het hoofd-onderwerp dat niet is."
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

    list_filter = [
        "gepubliceerd",
    ]

    def get_changelist_formset(self, request, **kwargs):
        kwargs["formset"] = OnderwerpAdminFormSet
        return super().get_changelist_formset(request, **kwargs)
