from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
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
        summary="Maak een PRODUCTTYPE aan.",
        description="Maak een PRODUCTTYPE aan.",
        examples=[
            OpenApiExample(
                "Create product type",
                value={
                    "uniforme_product_naam": "http://standaarden.overheid.nl/owms/terms/aanleunwoning",
                    "thema_ids": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                    "locatie_ids": ["235de068-a9c5-4eda-b61d-92fd7f09e9dc"],
                    "organisatie_ids": ["2c2694f1-f948-4960-8312-d51c3a0e540f"],
                    "contact_ids": ["6863d699-460d-4c1e-9297-16812d75d8ca"],
                    "gepubliceerd": False,
                    "naam": "Aanleunwoning",
                    "samenvatting": "korte samenvatting...",
                    "beschrijving": "uitgebreide beschrijving...",
                    "keywords": ["wonen"],
                },
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRODUCTTYPE in zijn geheel bij.",
        description="Werk een PRODUCTTYPE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRODUCTTYPE deels bij.",
        description="Werk een PRODUCTTYPE deels bij\nAls thema_ids, locatie_ids, organisatie_ids of contact_ids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRODUCTTYPE.",
        description="Verwijder een PRODUCTTYPE.",
    ),
)
class ProductTypeViewSet(OrderedModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gepubliceerd"]

    @extend_schema(
        "actuele_prijzen",
        summary="Alle ACTUELE PRIJZEN opvragen.",
        description="Geeft de huidige prijzen van alle PRODUCTTYPEN terug.",
    )
    @action(
        detail=False,
        serializer_class=ProductTypeActuelePrijsSerializer,
        url_path="actuele-prijzen",
    )
    def actuele_prijzen(self, request):
        product_typen = self.get_queryset().all()
        serializer = ProductTypeActuelePrijsSerializer(product_typen, many=True)
        return Response(serializer.data)

    @extend_schema(
        "actuele_prijs",
        summary="De actuele PRIJS van een PRODUCTTYPE opvragen.",
        description="Geeft de huidige prijzen van alle PRODUCTTYPEN terug.",
    )
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
        summary="Maak een LINK aan.",
        description="Maak een LINK aan.",
        examples=[
            OpenApiExample(
                "Create link",
                value={
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "naam": "Open Producten",
                    "url": "https://github.com/maykinmedia/open-producten",
                },
            )
        ],
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
        summary="Maak een PRIJS aan.",
        description="Maak een PRIJS aan.",
        examples=[
            OpenApiExample(
                "Create prijs",
                description="prijsOptie bedragen kunnen worden ingevuld als een getal of als string met een . of , voor de decimalen",
                value={
                    "prijsopties": [
                        {"bedrag": "50,99", "beschrijving": "normaal"},
                        {"bedrag": "70,99", "beschrijving": "spoed"},
                    ],
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "actief_vanaf": "2024-12-01",
                },
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRIJS in zijn geheel bij.",
        description="Werk een PRIJS in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRIJS deels bij.",
        description="Werk een PRIJS deels bij.\nAls prijsopties in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
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
        summary="Maak een VRAAG aan.",
        description="Maak een VRAAG aan.",
        examples=[
            OpenApiExample(
                "Create vraag",
                value={
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "vraag": "Kom ik in aanmerking voor dit product?",
                    "antwoord": "Ja",
                },
            )
        ],
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


@extend_schema_view(
    list=extend_schema(
        summary="Alle BESTANDEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek BESTAND opvragen.",
        description="Een specifieke BESTAND opvragen.",
    ),
    create=extend_schema(
        summary="Maak een BESTAND aan.",
        description="Maak een BESTAND aan.",
        examples=[
            OpenApiExample(
                "Create bestand",
                value={
                    "bestand": "test.txt",
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                },
                media_type="multipart/form-data",
            ),
        ],
    ),
    update=extend_schema(
        summary="Werk een BESTAND in zijn geheel bij.",
        description="Werk een BESTAND in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een BESTAND deels bij.",
        description="Werk een BESTAND deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een BESTAND.",
        description="Verwijder een BESTAND.",
    ),
)
class BestandViewSet(OrderedModelViewSet):
    queryset = Bestand.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = BestandSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product_type_id"]


@extend_schema_view(
    list=extend_schema(
        summary="Alle THEMA'S opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek THEMA opvragen.",
        description="Een specifieke THEMA opvragen.",
    ),
    create=extend_schema(
        summary="Maak een THEMA aan.",
        description="Maak een THEMA aan.",
        examples=[
            OpenApiExample(
                "Create thema",
                value={
                    "hoofd_thema": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
                    "product_type_ids": ["95792000-d57f-4d3a-b14c-c4c7aa964907"],
                    "gepubliceerd": True,
                    "naam": "Parkeren",
                    "beschrijving": "Parkeren in gemeente ABC",
                },
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een THEMA in zijn geheel bij.",
        description="Werk een THEMA in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een THEMA deels bij.",
        description="Werk een THEMA deels bij.\nAls product_type_ids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een THEMA.",
        description="Verwijder een THEMA.",
    ),
)
class ThemaViewSet(OrderedModelViewSet):
    queryset = Thema.objects.all()
    serializer_class = ThemaSerializer
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
