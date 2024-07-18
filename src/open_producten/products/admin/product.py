from django.contrib import admin

from open_producten.products.models import Product

from .data import DataInline


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_type_name",
        "created_on",
        "start_date",
        "end_date",
        "bsn",
        "kvk",
    )
    list_filter = ("product_type__name", "created_on", "start_date", "end_date")
    autocomplete_fields = ("product_type",)
    search_fields = ("product_type__name",)
    inlines = (DataInline,)
