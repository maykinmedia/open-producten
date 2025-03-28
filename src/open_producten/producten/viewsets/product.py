from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from notifications_api_common.viewsets import NotificationViewSetMixin

from open_producten.logging.api_tools import AuditTrailViewSetMixin
from open_producten.producten.kanalen import KANAAL_PRODUCTEN
from open_producten.producten.models import Product
from open_producten.producten.serializers.product import ProductSerializer
from open_producten.utils.filters import FilterSet, TranslationFilter
from open_producten.utils.views import OrderedModelViewSet


class ProductFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="producttype__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )

    producttype__naam = TranslationFilter(
        field_name="producttype__naam",
        lookup_expr="exact",
        help_text=_("Naam van het producttype."),
    )

    class Meta:
        model = Product
        fields = {
            "gepubliceerd": ["exact"],
            "status": ["exact"],
            "frequentie": ["exact"],
            "prijs": ["exact", "gte", "lte"],
            "producttype__code": ["exact"],
            "producttype__id": ["exact"],
            "start_datum": ["exact", "gte", "lte"],
            "eind_datum": ["exact", "gte", "lte"],
            "aanmaak_datum": ["exact", "gte", "lte"],
            "update_datum": ["exact", "gte", "lte"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRODUCTEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek PRODUCT opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRODUCT aan.",
    ),
    update=extend_schema(
        summary="Werk een PRODUCT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRODUCT deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRODUCT.",
    ),
)
class ProductViewSet(
    AuditTrailViewSetMixin, NotificationViewSetMixin, OrderedModelViewSet
):
    queryset = Product.objects.all()
    lookup_url_field = "id"
    serializer_class = ProductSerializer
    filterset_class = ProductFilterSet
    notifications_kanaal = KANAAL_PRODUCTEN
