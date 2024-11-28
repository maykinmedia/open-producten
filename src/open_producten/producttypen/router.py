from django.urls import include, path

from rest_framework_nested.routers import DefaultRouter, NestedSimpleRouter

from open_producten.producttypen.views import (
    OnderwerpViewSet,
    OnderwerpVraagViewSet,
    ProductTypeLinkViewSet,
    ProductTypePrijsViewSet,
    ProductTypeViewSet,
    ProductTypeVraagViewSet,
)

ProductTypenRouter = DefaultRouter()
ProductTypenRouter.register("producttypen", ProductTypeViewSet, basename="producttype")

ProductTypenLinkRouter = NestedSimpleRouter(
    ProductTypenRouter, "producttypen", lookup="product_type"
)
ProductTypenLinkRouter.register(
    r"links", ProductTypeLinkViewSet, basename="producttype-link"
)

ProductTypenPrijsRouter = NestedSimpleRouter(
    ProductTypenRouter, "producttypen", lookup="product_type"
)
ProductTypenPrijsRouter.register(
    r"prijzen", ProductTypePrijsViewSet, basename="producttype-prijs"
)

ProductTypenVraagRouter = NestedSimpleRouter(
    ProductTypenRouter, "producttypen", lookup="product_type"
)
ProductTypenVraagRouter.register(
    r"vragen", ProductTypeVraagViewSet, basename="producttype-vraag"
)

ProductTypenRouter.register("onderwerpen", OnderwerpViewSet, basename="onderwerp")

OnderwerpenVraagRouter = NestedSimpleRouter(
    ProductTypenRouter, "onderwerpen", lookup="onderwerp"
)
OnderwerpenVraagRouter.register(
    r"vragen", OnderwerpVraagViewSet, basename="onderwerp-vraag"
)

product_type_urlpatterns = [
    path("", include(ProductTypenRouter.urls)),
    path("", include(ProductTypenLinkRouter.urls)),
    path("", include(ProductTypenPrijsRouter.urls)),
    path("", include(ProductTypenVraagRouter.urls)),
    path("", include(OnderwerpenVraagRouter.urls)),
]
