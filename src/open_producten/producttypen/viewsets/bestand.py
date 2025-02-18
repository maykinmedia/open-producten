import django_filters
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser

from open_producten.producttypen.models import Bestand
from open_producten.producttypen.serializers import BestandSerializer
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet


class BestandFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="product_type__uniforme_product_naam__naam", lookup_expr="exact"
    )
    naam__contains = django_filters.CharFilter(
        field_name="bestand", lookup_expr="contains"
    )

    class Meta:
        model = Bestand
        fields = {
            "product_type__code": ["exact"],
            "product_type__id": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle BESTANDEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek BESTAND opvragen.",
    ),
    create=extend_schema(
        summary="Maak een BESTAND aan.",
        examples=[
            OpenApiExample(
                "Create bestand",
                value={
                    "bestand": "test.txt",
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                },
                media_type="multipart/form-data",
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Werk een BESTAND in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een BESTAND deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een BESTAND.",
    ),
)
class BestandViewSet(OrderedModelViewSet):
    queryset = Bestand.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = BestandSerializer
    lookup_url_kwarg = "id"
    filterset_class = BestandFilterSet
