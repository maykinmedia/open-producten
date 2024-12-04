from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from open_producten.producttypen.models import (
    Bestand,
    Link,
    Prijs,
    ProductType,
    Thema,
    Vraag,
)
from open_producten.producttypen.serializers import (
    BestandSerializer,
    LinkSerializer,
    PrijsSerializer,
    ProductTypeActuelePrijsSerializer,
    ProductTypeSerializer,
    ThemaSerializer,
    VraagSerializer,
)
from open_producten.utils.views import OrderedModelViewSet


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRODUCTTYPEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek PRODUCTTYPE opvragen.",
        description="Een specifiek PRODUCTTYPE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRODUCTTYPE aan.", description="Maak een PRODUCTTYPE aan."
    ),
    update=extend_schema(
        summary="Werk een PRODUCTTYPE in zijn geheel bij.",
        description="Werk een PRODUCTTYPE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een LINK deels bij.",
        description="Werk een LINK deels bij",
    ),
    destroy=extend_schema(
        summary="Verwijder een LINK.",
        description="Verwijder een LINK.",
    ),
)
class ProductTypeViewSet(OrderedModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd"]

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


@extend_schema_view(
    list=extend_schema(
        summary="Alle LINKS opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke LINK opvragen.",
        description="Een specifieke LINK opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LINK aan.", description="Maak een LINK aan."
    ),
    update=extend_schema(
        summary="Werk een LINK in zijn geheel bij.",
        description="Werk een LINK in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een LINK deels bij.",
        description="Werk een LINK deels bij",
    ),
    destroy=extend_schema(
        summary="Verwijder een LINK.",
        description="Verwijder een LINK.",
    ),
)
class LinkViewSet(OrderedModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id"]


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRIJZEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke PRIJS opvragen.",
        description="Een specifieke PRIJS opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRIJS aan.", description="Maak een PRIJS aan."
    ),
    update=extend_schema(
        summary="Werk een PRIJS in zijn geheel bij.",
        description="Werk een PRIJS in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRIJS deels bij.", description="Werk een PRIJS deels bij."
    ),
    destroy=extend_schema(
        summary="Verwijder een PRIJS.",
        description="Verwijder een PRIJS.",
    ),
)
class PrijsViewSet(OrderedModelViewSet):
    queryset = Prijs.objects.all()
    serializer_class = PrijsSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id"]


@extend_schema_view(
    list=extend_schema(
        summary="Alle VRAGEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke VRAAG opvragen.",
        description="Een specifieke VRAAG opvragen.",
    ),
    create=extend_schema(
        summary="Maak een VRAAG aan.", description="Maak een VRAAG aan."
    ),
    update=extend_schema(
        summary="Werk een VRAAG in zijn geheel bij.",
        description="Werk een VRAAG in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een VRAAG deels bij.", description="Werk een VRAAG deels bij."
    ),
    destroy=extend_schema(
        summary="Verwijder een VRAAG.",
        description="Verwijder een VRAAG.",
    ),
)
class VraagViewSet(OrderedModelViewSet):
    queryset = Vraag.objects.all()
    serializer_class = VraagSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id", "thema_id"]


class BestandViewSet(OrderedModelViewSet):
    queryset = Bestand.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = BestandSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id"]


class ThemaViewSet(OrderedModelViewSet):
    queryset = Thema.objects.all()
    serializer_class = ThemaSerializer
@extend_schema_view(
    list=extend_schema(
        summary="Alle ONDERWERPEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek ONDERWERP opvragen.",
        description="Een specifieke ONDERWERP opvragen.",
    ),
    create=extend_schema(
        summary="Maak een ONDERWERP aan.", description="Maak een ONDERWERP aan."
    ),
    update=extend_schema(
        summary="Werk een ONDERWERP in zijn geheel bij.",
        description="Werk een ONDERWERP in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een ONDERWERP deels bij.",
        description="Werk een ONDERWERP deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een ONDERWERP.",
        description="Verwijder een ONDERWERP.",
    ),
)
class OnderwerpViewSet(OrderedModelViewSet):
    queryset = Onderwerp.objects.all()
    serializer_class = OnderwerpSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        errors = []
        for product_type in ProductType.objects.filter(themas__in=[instance]):
            if product_type.themas.count() <= 1:
                errors.append(
                    _(
                        "Product Type {} moet aan een minimaal één thema zijn gelinkt."
                    ).format(product_type)
                )

        if errors:
            return Response(
                data={"product_typen": errors}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                data={
                    "sub_themas": [
                        _(
                            "Dit thema kan niet worden verwijderd omdat er gerelateerde sub_themas zijn."
                        )
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
