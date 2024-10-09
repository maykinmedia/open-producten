from open_producten.locations.models import (
    Contact,
    Location,
    Neighbourhood,
    Organisation,
    OrganisationType,
)
from open_producten.locations.serializers.location import (
    ContactSerializer,
    LocationSerializer,
    NeighbourhoodSerializer,
    OrganisationSerializer,
    OrganisationTypeSerializer,
)
from open_producten.utils.views import OrderedModelViewSet


class LocationViewSet(OrderedModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    lookup_field = "id"


class ContactViewSet(OrderedModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = "id"


class OrganisationViewSet(OrderedModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    lookup_field = "id"


class NeighbourhoodViewSet(OrderedModelViewSet):
    queryset = Neighbourhood.objects.all()
    serializer_class = NeighbourhoodSerializer
    lookup_field = "id"


class OrganisationTypeViewSet(OrderedModelViewSet):
    queryset = OrganisationType.objects.all()
    serializer_class = OrganisationTypeSerializer
    lookup_field = "id"
