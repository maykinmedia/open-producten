from open_producten.locaties.models import Contact, Locatie, Organisatie
from open_producten.locaties.serializers.locatie import (
    ContactSerializer,
    LocatieSerializer,
    OrganisatieSerializer,
)
from open_producten.utils.views import OrderedModelViewSet


class LocatieViewSet(OrderedModelViewSet):
    queryset = Locatie.objects.all()
    serializer_class = LocatieSerializer
    lookup_field = "id"


class ContactViewSet(OrderedModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = "id"


class OrganisatieViewSet(OrderedModelViewSet):
    queryset = Organisatie.objects.all()
    serializer_class = OrganisatieSerializer
    lookup_field = "id"
