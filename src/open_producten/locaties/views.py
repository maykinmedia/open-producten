from drf_spectacular.utils import extend_schema, extend_schema_view

from open_producten.locaties.models import Contact, Locatie, Organisatie
from open_producten.locaties.serializers.locatie import (
    ContactSerializer,
    LocatieSerializer,
    OrganisatieSerializer,
)
from open_producten.utils.views import OrderedModelViewSet


@extend_schema_view(
    list=extend_schema(
        summary="Alle LOCATIES opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek LOCATIE opvragen.",
        description="Een specifieke LOCATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LOCATIE aan.", description="Maak een LOCATIE aan."
    ),
    update=extend_schema(
        summary="Werk een LOCATIE in zijn geheel bij.",
        description=("Werk een LOCATIE in zijn geheel bij."),
    ),
    partial_update=extend_schema(
        summary="Werk een LOCATIE deels bij.", description="Werk een LOCATIE deels bij."
    ),
    destroy=extend_schema(
        summary="Verwijder een LOCATIE.",
        description="Verwijder een LOCATIE.",
    ),
)
class LocatieViewSet(OrderedModelViewSet):
    queryset = Locatie.objects.all()
    serializer_class = LocatieSerializer
    lookup_field = "id"


@extend_schema_view(
    list=extend_schema(
        summary="Alle CONTACTEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek CONTACT opvragen.",
        description="Een specifieke CONTACT opvragen.",
    ),
    create=extend_schema(
        summary="Maak een CONTACT aan.", description="Maak een CONTACT aan."
    ),
    update=extend_schema(
        summary="Werk een CONTACT in zijn geheel bij.",
        description="Werk een CONTACT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een CONTACT deels bij.", description="Werk een CONTACT deels bij."
    ),
    destroy=extend_schema(
        summary="Verwijder een CONTACT.",
        description="Verwijder een CONTACT.",
    ),
)
class ContactViewSet(OrderedModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = "id"


@extend_schema_view(
    list=extend_schema(
        summary="Alle ORGANISATIES opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek ORGANISATIE opvragen.",
        description="Een specifieke ORGANISATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een ORGANISATIE aan.", description="Maak een ORGANISATIE aan."
    ),
    update=extend_schema(
        summary="Werk een ORGANISATIE in zijn geheel bij.",
        description="Werk een ORGANISATIE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een ORGANISATIE deels bij.",
        description="Werk een ORGANISATIE deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een ORGANISATIE.",
        description="Verwijder een ORGANISATIE.",
    ),
)
class OrganisatieViewSet(OrderedModelViewSet):
    queryset = Organisatie.objects.all()
    serializer_class = OrganisatieSerializer
    lookup_field = "id"
