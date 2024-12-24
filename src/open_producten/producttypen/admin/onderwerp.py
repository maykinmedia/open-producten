from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ..models import Onderwerp, ProductType
from .vraag import VraagInline


class ProductTypeInline(admin.TabularInline):
    model = ProductType.onderwerpen.through
    extra = 0

    verbose_name = _("Product type")
    verbose_name_plural = _("Product typen")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Onderwerp)
class OnderwerpAdmin(admin.ModelAdmin):
    inlines = (
        VraagInline,
        ProductTypeInline,
    )
    search_fields = ("naam", "hoofd_onderwerp__naam")
    list_display = ("naam", "hoofd_onderwerp", "gepubliceerd", "product_typen_count")

    @admin.display(description=_("Aantal product typen"))
    def product_typen_count(self, obj):
        return obj.product_typen_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(product_typen_count=Count("product_typen"))
        return queryset

    list_filter = ["gepubliceerd", "product_typen", "hoofd_onderwerp"]

    def get_deleted_objects(self, objs, request):
        """
        Product_typen need at least one onderwerp.
        """

        def get_product_type_url(instance):
            return reverse("admin:producttypen_producttype_change", args=(instance.id,))

        def get_current_product_type_onderwerpen(instance):
            return ", ".join(instance.onderwerpen.values_list("naam", flat=True))

        errors = []
        for product_type in ProductType.objects.filter(onderwerpen__in=objs).distinct():
            if product_type.onderwerpen.count() <= objs.count():
                errors.append(
                    format_html(
                        "Product Type <a href='{}'>{}</a> moet aan een minimaal één onderwerp zijn gelinkt. Huidige onderwerpen: {}.",
                        get_product_type_url(product_type),
                        product_type,
                        get_current_product_type_onderwerpen(product_type),
                    )
                )
        if errors:
            return [], [], [], errors
        return super().get_deleted_objects(objs, request)
