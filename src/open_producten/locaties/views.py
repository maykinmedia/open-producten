from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

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
        summary="Een specifieke LOCATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LOCATIE aan.",
        examples=[
            OpenApiExample(
                "Create locatie",
                value={
                    "naam": "Maykin Media",
                    "email": "info@maykinmedia.nl",
                    "telefoonnummer": "+310207530523",
                    "straat": "Kingsfortweg",
                    "huisnummer": "151",
                    "postcode": "1043GR",
                    "stad": "Amsterdam",
                },
                request_only=True,
            )
        ],
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
    filterset_fields = {
        "naam": ["iexact"],
        "email": ["iexact"],
        "telefoonnummer": ["contains"],
        "straat": ["iexact"],
        "huisnummer": ["iexact"],
        "postcode": ["exact"],
        "stad": ["iexact"],
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
        examples=[
            OpenApiExample(
                "Create contact",
                value={
                    "organisatie_id": "73a745d4-7df0-4510-991e-abfb19f0d861",
                    "voornaam": "Bob",
                    "achternaam": "de Vries",
                    "email": "bob@example.com",
                    "telefoonnummer": "0611223344",
                    "rol": "medewerker",
                },
                request_only=True,
            ),
        ],
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
    filterset_fields = {
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
        summary="Alle ORGANISATIES opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke ORGANISATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een ORGANISATIE aan.",
        examples=[
            OpenApiExample(
                "Create organisatie",
                value={
                    "naam": "Maykin Media",
                    "code": "org-1234",
                    "email": "info@maykinmedia.nl",
                    "telefoonnummer": "+310207530523",
                    "straat": "Kingsfortweg",
                    "huisnummer": "151",
                    "postcode": "1043GR",
                    "stad": "Amsterdam",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een ORGANISATIE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een ORGANISATIE deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een ORGANISATIE.",
    ),
)
class OrganisatieViewSet(OrderedModelViewSet):
    queryset = Organisatie.objects.all()
    serializer_class = OrganisatieSerializer
    lookup_field = "id"
    filterset_fields = {
        "naam": ["iexact"],
        "email": ["iexact"],
        "telefoonnummer": ["contains"],
        "straat": ["iexact"],
        "huisnummer": ["iexact"],
        "postcode": ["exact"],
        "stad": ["iexact"],
        "code": ["exact"],
    }
