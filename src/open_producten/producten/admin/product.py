from django.contrib import admin

from open_producten.producten.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_type_name",
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "bsn",
        "kvk",
    )
    list_filter = ("product_type__naam", "aanmaak_datum", "start_datum", "eind_datum")
    autocomplete_fields = ("product_type",)
    search_fields = ("product_type__naam",)

    @admin.display(description="Product Type")
    def product_type_name(self, obj):
        return obj.product_type.name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")
