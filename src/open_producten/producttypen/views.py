from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from open_producten.producttypen.models import (
    Link,
    Onderwerp,
    Prijs,
    ProductType,
    Vraag,
)
from open_producten.producttypen.serializers import (
    LinkSerializer,
    OnderwerpSerializer,
    PrijsSerializer,
    ProductTypeActuelePrijsSerializer,
    ProductTypeSerializer,
    VraagSerializer,
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
        product_typen = self.get_queryset().all()
        serializer = ProductTypeActuelePrijsSerializer(product_typen, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        serializer_class=ProductTypeActuelePrijsSerializer,
        url_path="actuele-prijs",
    )
    def actuele_prijs(self, request, id=None):
        product_type = self.get_object()
        serializer = ProductTypeActuelePrijsSerializer(product_type)
        return Response(serializer.data)


class LinkViewSet(OrderedModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id"]


class PrijsViewSet(OrderedModelViewSet):
    queryset = Prijs.objects.all()
    serializer_class = PrijsSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id"]


class VraagViewSet(OrderedModelViewSet):
    queryset = Vraag.objects.all()
    serializer_class = VraagSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id", "onderwerp_id"]


class OnderwerpViewSet(OrderedModelViewSet):
    queryset = Onderwerp.objects.all()
    serializer_class = OnderwerpSerializer
    lookup_url_kwarg = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        errors = []
        for product_type in ProductType.objects.filter(onderwerpen__in=[instance]):
            if product_type.onderwerpen.count() <= 1:
                errors.append(
                    _(
                        "Product Type {} moet aan een minimaal één onderwerp zijn gelinkt."
                    ).format(product_type)
                )

        if errors:
            return Response(data={"product_typen": errors}, status=400)
        return super().destroy(request, *args, **kwargs)
