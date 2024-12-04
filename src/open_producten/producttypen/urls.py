from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from vng_api_common.routers import DefaultRouter

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
    # "SERVERS": [{"url": "/producttypen/api/v0.0.1"}],
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
            urlconf="open_producten.producttypen.urls",
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
    path("", include(ProductTypenRouter.urls)),
    path("", include(LocatieRouter.urls)),
]
