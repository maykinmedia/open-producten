from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework.routers import DefaultRouter

from open_producten.producten.views import ProductViewSet

ProductRouter = DefaultRouter()
ProductRouter.register("producten", ProductViewSet, basename="product")

description = """
Een Api voor Producten.

Een product is de instantie van een Product type (zie producttypen api), hierin worden de specifieke gegevens van de instantie opgeslagen zoals bijvoorbeeld de gegevens van de eigenaar.

"""

custom_settings = {
    "TITLE": "Producten API",
    "VERSION": settings.PRODUCTEN_API_VERSION,
    "DESCRIPTION": description,
    "SERVERS": [{"url": f"/producten/api/v{settings.PRODUCTEN_API_MAJOR_VERSION}"}],
    "TAGS": [
        {
            "name": "producten",
            "description": "Opvragen en bewerken van PRODUCTEN.\n\n"
            "De status opties van een PRODUCT zijn afhankelijk van de `toegestane_statussen` van het product_type.\n\n"
            "Via `start_datum` & `eind_datum` kan de status van een product automatisch op ACTIEF en VERLOPEN worden gezet."
            "Op het moment dat deze velden worden gezet moeten deze statussen wel zijn toegestaan op het product_type.\n\n"
            "De status zal via de start_datum alleen naar ACTIEF veranderen mits de status INITIEEL of GEREED is. Voor de eind_datum zijn dit INTIEEL, GEREED of ACTIEF.",
        },
    ],
}


urlpatterns = [
    # API documentation
    path(
        "schema/openapi.yaml",
        SpectacularAPIView.as_view(
            urlconf="open_producten.producten.urls",
            custom_settings=custom_settings,
        ),
        name="schema-producten",
    ),
    path(
        "schema/",
        SpectacularRedocView.as_view(
            url_name="schema-producten", title=custom_settings["TITLE"]
        ),
        name="schema-redoc-producten",
    ),
    # actual API
    path("", include(ProductRouter.urls)),
]
