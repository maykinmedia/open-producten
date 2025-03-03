from drf_spectacular.utils import extend_schema, extend_schema_view

from open_producten.locaties.models import Locatie
from open_producten.locaties.serializers import LocatieSerializer
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet


class LocatieFilterSet(FilterSet):

    class Meta:
        model = Locatie
        fields = {
            "naam": ["iexact"],
            "email": ["iexact"],
            "telefoonnummer": ["contains"],
            "straat": ["iexact"],
            "huisnummer": ["iexact"],
            "postcode": ["exact"],
            "stad": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle LOCATIES opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek LOCATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LOCATIE aan.",
    ),
    update=extend_schema(
        summary="Werk een LOCATIE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een LOCATIE deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een LOCATIE.",
    ),
)
class LocatieViewSet(OrderedModelViewSet):
    queryset = Locatie.objects.all()
    serializer_class = LocatieSerializer
    lookup_field = "id"
    filterset_class = LocatieFilterSet
