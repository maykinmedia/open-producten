from django.core.validators import RegexValidator
from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from open_producten.producttypen.models import (
    Bestand,
    ContentElement,
    ContentLabel,
    JsonSchema,
    Link,
    Prijs,
    ProductType,
    Thema,
)
from open_producten.producttypen.serializers import (
    BestandSerializer,
    JsonSchemaSerializer,
    LinkSerializer,
    PrijsSerializer,
    ProductTypeActuelePrijsSerializer,
    ProductTypeSerializer,
    ThemaSerializer,
)
from open_producten.producttypen.serializers.content import (
    ContentElementSerializer,
    ContentElementTranslationSerializer,
    ContentLabelSerializer,
    NestedContentElementSerializer,
)
from open_producten.producttypen.serializers.producttype import (
    ProductTypeTranslationSerializer,
)
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet, TranslatableViewSetMixin


class ProductTypeFilterSet(FilterSet):
    regex = r"^\[([^:\[\]]+):([^:\[\]]+)\]$"  # [key:value] where the key and value cannot contain `[`, `]` or `:`

    externe_code = django_filters.CharFilter(
        method="filter_by_externe_code",
        validators=[RegexValidator(regex)],
        help_text=_("Producttype codes uit externe omgevingen. [naam:code]"),
    )

    parameter = django_filters.CharFilter(
        method="filter_by_parameter",
        validators=[RegexValidator(regex)],
        help_text=_("Producttype parameters. [naam:waarde]"),
    )

    uniforme_product_naam = django_filters.CharFilter(
        field_name="uniforme_product_naam__naam",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )

    def filter_by_externe_code(self, queryset, name, value):
        values = self.request.GET.getlist(name)

        for val in values:
            value_list = val.strip("[]").split(":")
            if len(value_list) != 2:
                raise ParseError(_("Invalid format for externe_code query parameter."))

            naam, code = value_list
            queryset = queryset.filter(
                externe_codes__naam=naam, externe_codes__code=code
            )
        return queryset

    def filter_by_parameter(self, queryset, name, value):
        values = self.request.GET.getlist(name)

        for val in values:
            value_list = val.strip("[]").split(":")
            if len(value_list) != 2:
                raise ParseError(_("Invalid format for parameter query parameter."))

            naam, waarde = value_list
            queryset = queryset.filter(parameters__naam=naam, parameters__waarde=waarde)
        return queryset

    class Meta:
        model = ProductType
        fields = ("gepubliceerd",)


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRODUCTTYPEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek PRODUCTTYPE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRODUCTTYPE aan.",
        examples=[
            OpenApiExample(
                "Create producttype",
                value={
                    "uniforme_product_naam": "aanleunwoning",
                    "thema_ids": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                    "locatie_ids": ["235de068-a9c5-4eda-b61d-92fd7f09e9dc"],
                    "organisatie_ids": ["2c2694f1-f948-4960-8312-d51c3a0e540f"],
                    "contact_ids": ["6863d699-460d-4c1e-9297-16812d75d8ca"],
                    "gepubliceerd": False,
                    "naam": "Aanleunwoning",
                    "code": "PT-12345",
                    "toegestane_statussen": ["gereed", "actief"],
                    "interne_opmerkingen": "interne opmerkingen...",
                    "samenvatting": "korte samenvatting...",
                    "beschrijving": "uitgebreide beschrijving...",
                    "keywords": ["wonen"],
                    "externe_codes": [
                        {"naam": "ISO", "code": "123"},
                        {"naam": "CBS", "code": "456"},
                    ],
                    "parameters": [
                        {"naam": "doelgroep", "waarde": "inwoners"},
                    ],
                    "verbruiksobject_schema_naam": "verbruik_schema",
                    "dataobject_schema": "data_schema",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRODUCTTYPE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRODUCTTYPE deels bij.",
        description="Als thema_ids, locatie_ids, organisatie_ids of contact_ids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRODUCTTYPE.",
    ),
)
class ProductTypeViewSet(TranslatableViewSetMixin, OrderedModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductTypeFilterSet

    @extend_schema(
        summary="De vertaling van een producttype aanpassen.",
        description="nl kan worden aangepast via het model.",
        parameters=[
            OpenApiParameter(
                name="taal",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @action(
        detail=True,
        methods=["put", "patch"],
        serializer_class=ProductTypeTranslationSerializer,
        url_path="vertaling/(?P<taal>[^/.]+)",
    )
    def vertaling(self, request, taal, **kwargs):
        return super().update_vertaling(request, taal, **kwargs)

    @extend_schema(
        summary="De vertaling van een producttype verwijderen.",
        description="nl kan niet worden verwijderd.",
        parameters=[
            OpenApiParameter(
                name="taal",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @vertaling.mapping.delete
    def delete_vertaling(self, request, taal, **kwargs):
        return super().delete_vertaling(request, taal, **kwargs)

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

    @extend_schema(
        "content",
        summary="De CONTENT van een PRODUCTTYPE opvragen.",
        description="Geeft de content van een PRODUCTTYPE terug.",
    )
    @action(
        detail=True,
        serializer_class=NestedContentElementSerializer,
        url_path="content",
    )
    def content(self, request, id=None):
        product_type = self.get_object()

        queryset = product_type.content_elementen

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Alle LINKS opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke LINK opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LINK aan.",
        examples=[
            OpenApiExample(
                "Create link",
                value={
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "naam": "Open Producten",
                    "url": "https://github.com/maykinmedia/open-producten",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een LINK in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een LINK deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een LINK.",
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
    ),
    create=extend_schema(
        summary="Maak een PRIJS aan.",
        examples=[
            OpenApiExample(
                "Create prijs",
                description="prijsOptie bedragen kunnen worden ingevuld als een getal of als string met een . of , voor de decimalen",
                value={
                    "prijsopties": [
                        {"bedrag": "50.99", "beschrijving": "normaal"},
                        {"bedrag": "70.99", "beschrijving": "spoed"},
                    ],
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "actief_vanaf": "2024-12-01",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRIJS in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRIJS deels bij.",
        description="Als prijsopties in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRIJS.",
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
        summary="Alle BESTANDEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek BESTAND opvragen.",
    ),
    create=extend_schema(
        summary="Maak een BESTAND aan.",
        examples=[
            OpenApiExample(
                "Create bestand",
                value={
                    "bestand": "test.txt",
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                },
                media_type="multipart/form-data",
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Werk een BESTAND in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een BESTAND deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een BESTAND.",
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
    ),
    create=extend_schema(
        summary="Maak een THEMA aan.",
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
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een THEMA in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een THEMA deels bij.",
        description="Als product_type_ids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een THEMA.",
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


@extend_schema_view(
    retrieve=extend_schema(
        summary="Een specifiek CONTENTELEMENT opvragen.",
    ),
    create=extend_schema(
        summary="Maak een CONTENTELEMENT aan.",
        examples=[
            OpenApiExample(
                "Create content",
                value={
                    "labels": ["openingstijden"],
                    "content": "ma-vr 8:00-17:00",
                    "product_type_id": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een CONTENTELEMENT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een CONTENTELEMENT deels bij.",
        description="Als product_type_ids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een CONTENTELEMENT.",
    ),
)
class ContentElementViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TranslatableViewSetMixin,
    GenericViewSet,
):
    queryset = ContentElement.objects.all()
    serializer_class = ContentElementSerializer
    lookup_url_kwarg = "id"

    @extend_schema(
        summary="De vertaling van een content element aanpassen.",
        description="nl kan worden aangepast via het model.",
        parameters=[
            OpenApiParameter(
                name="taal",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @action(
        detail=True,
        methods=["put"],
        serializer_class=ContentElementTranslationSerializer,
        url_path="vertaling/(?P<taal>[^/.]+)",
    )
    def vertaling(self, request, taal, **kwargs):
        return super().update_vertaling(request, taal, **kwargs)

    @extend_schema(
        summary="De vertaling van een content element verwijderen.",
        description="nl kan niet worden verwijderd.",
        parameters=[
            OpenApiParameter(
                name="taal",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @vertaling.mapping.delete
    def delete_vertaling(self, request, taal, **kwargs):
        return super().delete_vertaling(request, taal, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="Alle CONTENTELEMENTLABELS opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
)
class ContentLabelViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = ContentLabel.objects.all()
    serializer_class = ContentLabelSerializer
    lookup_field = "id"


@extend_schema_view(
    list=extend_schema(
        summary="Alle SCHEMA'S opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek SCHEMA opvragen.",
    ),
    create=extend_schema(
        summary="Maak een SCHEMA aan.",
        examples=[
            OpenApiExample(
                "Create schema",
                value={
                    "naam": "parkeervergunning-verbruiksobject",
                    "schema": {
                        "type": "object",
                        "properties": {"uren": {"type": "number"}},
                        "required": ["uren"],
                    },
                },
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Werk een SCHEMA in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een SCHEMA deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een SCHEMA.",
    ),
)
class JsonSchemaViewSet(OrderedModelViewSet):
    queryset = JsonSchema.objects.all()
    serializer_class = JsonSchemaSerializer
    lookup_url_kwarg = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["naam"]
