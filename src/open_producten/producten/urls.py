from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework_nested.routers import DefaultRouter

from open_producten.producten.views import ProductViewSet

ProductRouter = DefaultRouter()
ProductRouter.register("producten", ProductViewSet, basename="product")

custom_settings = {
    "TITLE": "Producten API",
    "VERSION": settings.PRODUCTEN_API_VERSION,
    # "DESCRIPTION": description,
    # TODO is this needed?  "SERVERS": [{"url": "/producten/api/v1"}],
    "TAGS": [{"name": "producten"}],
}


urlpatterns = [
    # API documentation
    path(
        "schema/openapi.yaml",
        SpectacularAPIView.as_view(
            urlconf="open_producten.producten.router",
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
