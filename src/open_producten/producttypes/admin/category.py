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


class CategoryAdminFormSet(BaseModelFormSet):
    def clean(self):
        for row in self.cleaned_data:
            current_node = row["id"]
            children = current_node.get_children()
            if children:
                if not row["published"] and children.published().exists():
                    raise forms.ValidationError(
                        _(
                            "Parent nodes cannot be unpublished if they have published children."
                        )
                    )
            if (
                row["published"]
                and not current_node.is_root()
                and not current_node.get_parent().published
            ):
                raise forms.ValidationError(
                    _("Parent nodes have to be published in order to publish a child.")
                )
        return super().clean()


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = CategoryAdminForm
    inlines = (
        CategoryProductTypeInline,
        QuestionInline,
    )
    prepopulated_fields = {"slug": ("name",)}
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
                    "slug",
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
