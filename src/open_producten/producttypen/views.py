from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response

from open_producten.producttypen.models import (
    Link,
    Onderwerp,
    Prijs,
    ProductType,
    Vraag,
)
from open_producten.producttypen.serializers.children import (
    LinkSerializer,
    PrijsSerializer,
    VraagSerializer,
)
from open_producten.producttypen.serializers.onderwerp import OnderwerpSerializer
from open_producten.producttypen.serializers.producttype import (
    ProductTypeActuelePrijsSerializer,
    ProductTypeSerializer,
)
from open_producten.utils.views import OrderedModelViewSet


class ProductTypeViewSet(OrderedModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    lookup_url_kwarg = "id"

    @action(
        detail=False,
        serializer_class=ProductTypeActuelePrijsSerializer,
        url_path="actuele-prijzen",
    )
    def actuele_prijzen(self, request):
        product_typen = ProductType.objects.all()
        serializer = ProductTypeActuelePrijsSerializer(product_typen, many=True)
        return Response(serializer.data)


class ProductTypeChildViewSet(OrderedModelViewSet):

    def get_product_type(self):
        return get_object_or_404(ProductType, id=self.kwargs["product_type_id"])

    def get_queryset(self):
        return super().get_queryset().filter(product_type=self.get_product_type())

    def perform_create(self, serializer):
        serializer.save(product_type=self.get_product_type())


class ProductTypeLinkViewSet(ProductTypeChildViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_url_kwarg = "link_id"


class ProductTypePrijsViewSet(ProductTypeChildViewSet):
    queryset = Prijs.objects.all()
    serializer_class = PrijsSerializer
    lookup_url_kwarg = "prijs_id"


class ProductTypeVraagViewSet(ProductTypeChildViewSet):
    queryset = Vraag.objects.all()
    serializer_class = VraagSerializer
    lookup_url_kwarg = "vraag_id"


class OnderwerpViewSet(OrderedModelViewSet):
    queryset = Onderwerp.objects.all()
    serializer_class = OnderwerpSerializer
    lookup_url_kwarg = "id"


class OnderwerpChildViewSet(OrderedModelViewSet):

    def get_onderwerp(self):
        return get_object_or_404(Onderwerp, id=self.kwargs["onderwerp_id"])

    def get_queryset(self):
        return super().get_queryset().filter(onderwerp=self.get_onderwerp())

    def perform_create(self, serializer):
        serializer.save(onderwerp=self.get_onderwerp())


class OnderwerpVraagViewSet(OnderwerpChildViewSet):
    queryset = Vraag.objects.all()
    serializer_class = VraagSerializer
    lookup_url_kwarg = "vraag_id"
