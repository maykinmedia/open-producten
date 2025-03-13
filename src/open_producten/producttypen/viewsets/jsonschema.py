from drf_spectacular.utils import extend_schema, extend_schema_view

from open_producten.producttypen.models import JsonSchema
from open_producten.producttypen.serializers import JsonSchemaSerializer
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet


class JsonSchemaFilterSet(FilterSet):

    class Meta:
        model = JsonSchema
        fields = {"naam": ["exact", "contains"]}


@extend_schema_view(
    list=extend_schema(
        summary="Alle SCHEMA'S opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek SCHEMA opvragen.",
    ),
    create=extend_schema(
        summary="Maak een SCHEMA aan.",
    ),
    update=extend_schema(
        summary="Werk een SCHEMA in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een SCHEMA deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een SCHEMA.",
    ),
)
class JsonSchemaViewSet(OrderedModelViewSet):
    queryset = JsonSchema.objects.all()
    serializer_class = JsonSchemaSerializer
    lookup_url_kwarg = "id"
    filterset_class = JsonSchemaFilterSet
