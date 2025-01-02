from django.urls import include, path

from rest_framework.routers import DefaultRouter

from open_producten.producttypen.views import (
    BestandViewSet,
    LinkViewSet,
    PrijsViewSet,
    ProductTypeViewSet,
    ThemaViewSet,
    VraagViewSet,
)

ProductTypenRouter = DefaultRouter()
ProductTypenRouter.register("producttypen", ProductTypeViewSet, basename="producttype")

ProductTypenRouter.register(r"links", LinkViewSet, basename="link")

ProductTypenRouter.register(r"prijzen", PrijsViewSet, basename="prijs")

ProductTypenRouter.register(r"vragen", VraagViewSet, basename="vraag")

ProductTypenRouter.register("themas", ThemaViewSet, basename="thema")

ProductTypenRouter.register("bestanden", BestandViewSet, basename="bestand")

product_type_urlpatterns = [
    path("", include(ProductTypenRouter.urls)),
]
