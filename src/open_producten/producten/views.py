from django_filters.rest_framework import DjangoFilterBackend

from open_producten.producten.models import Product
from open_producten.producten.serializers.product import (
    ProductSerializer,
    ProductUpdateSerializer,
)
from open_producten.utils.views import OrderedModelViewSet


class ProductViewSet(OrderedModelViewSet):
    queryset = Product.objects.all()
    lookup_url_field = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd"]

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return ProductUpdateSerializer
        return ProductSerializer
