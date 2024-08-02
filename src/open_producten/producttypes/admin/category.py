from django import forms
from django.contrib import admin
from django.forms import BaseModelFormSet
from django.utils.translation import gettext as _

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from ..models import Category, CategoryProductType
from .question import QuestionInline


class CategoryProductTypeInline(admin.TabularInline):
    model = CategoryProductType
    fields = ("product_type",)
    extra = 1


class CategoryAdminForm(movenodeform_factory(Category)):
    class Meta:
        model = Category
        fields = "__all__"

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        published = cleaned_data["published"]
        ref_node = cleaned_data["_ref_node_id"]
        if published and ref_node:
            parent_node = Category.objects.get(id=ref_node)
            if not parent_node.published:
                raise forms.ValidationError(
                    _("Parent nodes have to be published in order to publish a child.")
                )

        if (
            not published
            and self.instance.get_children().filter(published=True).exists()
        ):
            raise forms.ValidationError(
                _("Parent nodes cannot be unpublished if they have published children.")
            )


class CategoryAdminFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        data = {
            form.cleaned_data["id"]: form.cleaned_data["published"]
            for form in self.forms
        }

        for category, published in data.items():
            children = category.get_children()

            if children:
                if not published and any([data[child] for child in children]):
                    raise forms.ValidationError(
                        _("Parent nodes cannot be unpublished with published children.")
                    )


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = CategoryAdminForm
    inlines = (
        CategoryProductTypeInline,
        QuestionInline,
    )
    search_fields = ("name",)
    list_display = (
        "name",
        "published",
    )
    list_editable = ("published",)
    exclude = ("path", "depth", "numchild")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "icon",
                    "image",
                    "_position",
                    "_ref_node_id",
                ),
            },
        ),
        (
            _("Category permissions"),
            {
                "fields": ("published",),
            },
        ),
    )

    list_filter = [
        "published",
    ]

    def get_changelist_formset(self, request, **kwargs):
        kwargs["formset"] = CategoryAdminFormSet
        return super().get_changelist_formset(request, **kwargs)
