from rest_framework.routers import DefaultRouter

from open_producten.locaties.viewsets import (
    ContactViewSet,
    LocatieViewSet,
    OrganisatieViewSet,
)

LocatieRouter = DefaultRouter()

LocatieRouter.register("locaties", LocatieViewSet, basename="locatie")
LocatieRouter.register("organisaties", OrganisatieViewSet, basename="organisatie")
LocatieRouter.register("contacten", ContactViewSet, basename="contact")
