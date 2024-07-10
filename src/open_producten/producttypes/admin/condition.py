from django.contrib import admin

from ..models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "question",
        "display_products",
    )
    list_filter = ("product_types__name",)
    search_fields = ("name",)

    def display_products(self, obj):
        return ", ".join(p.name for p in obj.products.all())

    display_products.short_description = "Product types"
