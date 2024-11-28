from django.urls import include, path

from rest_framework.routers import DefaultRouter

from open_producten.locaties.views import (
    ContactViewSet,
    LocatieViewSet,
    OrganisatieViewSet,
)

LocatieRouter = DefaultRouter()

LocatieRouter.register("locaties", LocatieViewSet, basename="locaties")
LocatieRouter.register("organisaties", OrganisatieViewSet, basename="organisaties")
LocatieRouter.register("contacten", ContactViewSet, basename="contacten")

locatie_urlpatterns = [
    path("", include(LocatieRouter.urls)),
]
