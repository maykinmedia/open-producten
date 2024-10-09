from django.urls import include, path

from rest_framework.routers import DefaultRouter

from open_producten.locations.views import (
    ContactViewSet,
    LocationViewSet,
    NeighbourhoodViewSet,
    OrganisationTypeViewSet,
    OrganisationViewSet,
)

LocationRouter = DefaultRouter()

LocationRouter.register("locations", LocationViewSet, basename="locations")
LocationRouter.register("organisations", OrganisationViewSet, basename="organisations")
LocationRouter.register("contacts", ContactViewSet, basename="contacts")
LocationRouter.register(
    "neighbourhoods", NeighbourhoodViewSet, basename="neighbourhoods"
)
LocationRouter.register(
    "organisationtypes", OrganisationTypeViewSet, basename="organisationtypes"
)

location_urlpatterns = [
    path("", include(LocationRouter.urls)),
]
