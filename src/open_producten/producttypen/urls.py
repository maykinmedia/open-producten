from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from open_producten.locaties.router import LocatieRouter
from open_producten.producttypen.views import (
    BestandViewSet,
    LinkViewSet,
    PrijsViewSet,
    ProductTypeViewSet,
    ThemaViewSet,
    VraagViewSet,
)

ProductTypenRouter = DefaultRouter()
ProductTypenRouter.register("producttypen", ProductTypeViewSet)

ProductTypenRouter.register("links", LinkViewSet, basename="link")

ProductTypenRouter.register("prijzen", PrijsViewSet, basename="prijs")

ProductTypenRouter.register("vragen", VraagViewSet, basename="vraag")

ProductTypenRouter.register("themas", ThemaViewSet, basename="thema")

ProductTypenRouter.register("bestanden", BestandViewSet, basename="bestand")

custom_settings = {
    "TITLE": "Product typen API",
    "VERSION": settings.PRODUCTTYPEN_API_VERSION,
    # "DESCRIPTION": description,
    "SERVERS": [
        {"url": f"/producttypen/api/v{settings.PRODUCTTYPEN_API_MAJOR_VERSION}"}
    ],
    "TAGS": [
        {"name": "onderwerpen"},
        {"name": "producttypen"},
        {"name": "prijzen"},
        {"name": "links"},
        {"name": "vragen"},
        {"name": "locaties"},
        {"name": "organisaties"},
        {"name": "contacten"},
    ],
}

urlpatterns = [
    # API documentation
    path(
        "schema/openapi.yaml",
        SpectacularAPIView.as_view(
            urlconf="open_producten.producttypen.router",
            custom_settings=custom_settings,
        ),
        name="schema-producttypen",
    ),
    path(
        "schema/",
        SpectacularRedocView.as_view(
            url_name="schema-producttypen", title=custom_settings["TITLE"]
        ),
        name="schema-redoc-producttypen",
    ),
    path(
        "schema-swagger",
        SpectacularSwaggerView.as_view(url_name="schema-producttypen", title="schema"),
    ),
    path("", include(ProductTypenRouter.urls)),
    path("", include(LocatieRouter.urls)),
]
