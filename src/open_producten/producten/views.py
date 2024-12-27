from django_filters.rest_framework import DjangoFilterBackend

from open_producten.producten.models import Product
from open_producten.producten.serializers.product import ProductSerializer
from open_producten.utils.views import OrderedModelViewSet


class ProductViewSet(OrderedModelViewSet):
    queryset = Product.objects.all()
    lookup_url_field = "id"
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd"]
