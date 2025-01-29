from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from open_producten.locaties.urls import LocatieRouter
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

description = """
Een Api voor Product typen.

Een Product type is de definitie van een Product. hierin word alle relevante data opgeslagen zoals informatie teksten bedoeld voor klanten.

Een Product (zie product api) is de instantie, hierin worden de specifieke gegevens van de instantie opgeslagen zoals bijvoorbeeld de gegevens van de eigenaar.

Een product type valt onder een thema. Een thema kan onderdeel zijn van een ander thema via het attribuut 'hoofd_thema'.

Een product type kan worden gelinkt één of meerdere locaties, organisaties en/of contacten.

Daarnaast kunnen de volgende modellen per product worden aangemaakt:
- prijzen
- links
- vragen

Een aantal velden verwachten een lijst/array van bijvoorbeeld product_type_ids. Let op dat als dit veld in een PATCH request wordt meegestuurd de gehele lijst/array zal worden overschreven.

"""

custom_settings = {
    "TITLE": "Product typen API",
    "VERSION": settings.PRODUCTTYPEN_API_VERSION,
    "DESCRIPTION": description,
    "SERVERS": [
        {"url": f"/producttypen/api/v{settings.PRODUCTTYPEN_API_MAJOR_VERSION}"}
    ],
    "TAGS": [
        {"name": "themas", "description": "Opvragen en bewerken van THEMA'S."},
        {
            "name": "producttypen",
            "description": "Opvragen en bewerken van PRODUCTTYPEN.",
        },
        {"name": "prijzen", "description": "Opvragen en bewerken van PRIJZEN."},
        {"name": "links", "description": "Opvragen en bewerken van LINKS."},
        {
            "name": "vragen",
            "description": "Opvragen en bewerken van VRAGEN. Een vraag kan gelinkt zijn aan een PRODUCTTYPE OF THEMA.",
        },
        {"name": "locaties", "description": "Opvragen en bewerken van LOCATIES."},
        {
            "name": "organisaties",
            "description": "Opvragen en bewerken van ORGANISATIES.",
        },
        {"name": "contacten", "description": "Opvragen en bewerken van CONTACTEN."},
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
    path(
        "schema-swagger",
        SpectacularSwaggerView.as_view(url_name="schema-producttypen", title="schema"),
    ),
    path("", include(ProductTypenRouter.urls)),
    path("", include(LocatieRouter.urls)),
]
