from django.urls import include, path

from rest_framework_nested.routers import DefaultRouter

from open_producten.producten.views import ProductViewSet

ProductRouter = DefaultRouter()
ProductRouter.register("producten", ProductViewSet, basename="product")

product_urlpatterns = [
    path("", include(ProductRouter.urls)),
]
