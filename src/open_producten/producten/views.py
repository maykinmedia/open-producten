from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from notifications_api_common.viewsets import NotificationViewSetMixin

from open_producten.logging.api_tools import AuditTrailViewSetMixin
from open_producten.producten.kanalen import KANAAL_PRODUCTEN
from open_producten.producten.models import Product
from open_producten.producten.serializers.product import ProductSerializer
from open_producten.utils.views import OrderedModelViewSet


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
        examples=[
            OpenApiExample(
                "Create product",
                value={
                    "start_datum": "2024-12-01",
                    "eind_datum": "2026-12-01",
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "gepubliceerd": False,
                    "bsn": "111222333",
                    "status": "gereed",
                    "prijs": "20.20",
                    "frequentie": "eenmalig",
                    "verbruiksobject": {"uren": 130},
                    "data": {"max_uren": 150},
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRODUCT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRODUCT deels bij.",
        examples=[
            OpenApiExample(
                "Patch product",
                value={
                    "gepubliceerd": True,
                    "start_datum": "2019-08-24",
                    "eind_datum": "2019-08-24",
                    "bsn": "string",
                    "status": "gereed",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Update product status",
                value={
                    "status": "actief",
                },
                request_only=True,
            ),
        ],
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd", "status", "frequentie"]
    notifications_kanaal = KANAAL_PRODUCTEN
