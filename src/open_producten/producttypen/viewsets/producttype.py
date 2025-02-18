import django_filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from open_producten.producttypen.models import ProductType
from open_producten.producttypen.serializers import (
    ProductTypeActuelePrijsSerializer,
    ProductTypeSerializer,
)
from open_producten.producttypen.serializers.content import (
    NestedContentElementSerializer,
)
from open_producten.producttypen.serializers.producttype import (
    ProductTypeTranslationSerializer,
)
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet, TranslatableViewSetMixin


class ProductTypeFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="uniforme_product_naam__naam", lookup_expr="exact"
    )

    class Meta:
        model = ProductType
        fields = {
            "code": ["exact"],
        }


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
                "Create product type",
                value={
                    "uniforme_product_naam": "http://standaarden.overheid.nl/owms/terms/aanleunwoning",
                    "thema_ids": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                    "locatie_ids": ["235de068-a9c5-4eda-b61d-92fd7f09e9dc"],
                    "organisatie_ids": ["2c2694f1-f948-4960-8312-d51c3a0e540f"],
                    "contact_ids": ["6863d699-460d-4c1e-9297-16812d75d8ca"],
                    "gepubliceerd": False,
                    "naam": "Aanleunwoning",
                    "code": "PT-12345",
                    "toegestane_statussen": ["gereed", "actief"],
                    "samenvatting": "korte samenvatting...",
                    "beschrijving": "uitgebreide beschrijving...",
                    "keywords": ["wonen"],
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
