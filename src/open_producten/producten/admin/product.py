from django import forms
from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _

from open_producten.logging.service import AdminAuditLogMixin, get_logs_link
from open_producten.producten.models import Product


class ProductAdminForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"] = forms.TypedChoiceField(
            label=_("status"),
            choices=self.instance.status_choices,
            widget=forms.Select,
        )


@admin.register(Product)
class ProductAdmin(AdminAuditLogMixin, admin.ModelAdmin):
    list_display = (
        "product_type_name",
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "status",
        "show_actions",
    )
    list_filter = (
        "product_type__naam",
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "status",
    )
    autocomplete_fields = ("product_type",)
    search_fields = ("product_type__naam",)
    form = ProductAdminForm

    @admin.display(description="Product Type")
    def product_type_name(self, obj):
        return obj.product_type.naam

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")

    @admin.display(description=_("actions"))
    def show_actions(self, obj: Product) -> str:
        actions = [
            get_logs_link(obj),
        ]
        return format_html_join(
            " | ",
            '<a href="{}">{}</a>',
            actions,
        )
