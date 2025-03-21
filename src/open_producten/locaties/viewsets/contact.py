from drf_spectacular.utils import extend_schema, extend_schema_view

from open_producten.locaties.models import Contact
from open_producten.locaties.serializers import ContactSerializer
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet


class ContactFilterSet(FilterSet):

    class Meta:
        model = Contact
        fields = {
            "organisatie__naam": ["exact"],
            "organisatie__id": ["exact"],
            "voornaam": ["exact"],
            "achternaam": ["exact"],
            "email": ["iexact"],
            "telefoonnummer": ["contains"],
            "rol": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle CONTACTEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek CONTACT opvragen.",
    ),
    create=extend_schema(
        summary="Maak een CONTACT aan.",
    ),
    update=extend_schema(
        summary="Werk een CONTACT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een CONTACT deels bij.", description="Werk een CONTACT deels bij."
    ),
    destroy=extend_schema(
        summary="Verwijder een CONTACT.",
    ),
)
class ContactViewSet(OrderedModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = "id"
    filterset_class = ContactFilterSet
