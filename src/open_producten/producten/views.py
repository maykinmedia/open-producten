from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

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
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRODUCT in zijn geheel bij.",
    ),
    partial_update=extend_schema(summary="Werk een PRODUCT deels bij."),
    destroy=extend_schema(
        summary="Verwijder een PRODUCT.",
    ),
)
class ProductViewSet(OrderedModelViewSet):
    queryset = Product.objects.all()
    lookup_url_field = "id"
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd"]
