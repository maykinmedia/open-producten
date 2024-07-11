from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext as _

from ..models import Category, ProductType
from .field import FieldInline
from .file import FileInline
from .link import LinkInline
from .question import QuestionInline


class ProductTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = "__all__"

    categories = forms.ModelMultipleChoiceField(
        label=_("Allowed admin categories"),
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_("Category"), is_stacked=False),
    )

    def clean(self):
        cleaned_data = super().clean()
        if len(cleaned_data["categories"]) == 0:
            self.add_error("categories", _("At least one category is required"))
        return cleaned_data


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_on", "display_categories", "published")
    list_filter = ("published", "categories", "tags")
    list_editable = ("published",)
    date_hierarchy = "created_on"
    autocomplete_fields = (
        "related_product_types",
        "tags",
        "conditions",
    )
    search_fields = ("name",)
    ordering = ("name",)
    save_on_top = True
    form = ProductTypeAdminForm
    inlines = (FileInline, LinkInline, QuestionInline, FieldInline)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.prefetch_related(
            "links",
        )

    def display_categories(self, obj):
        return ", ".join(p.name for p in obj.categories.all())

    display_categories.short_description = "categories"
