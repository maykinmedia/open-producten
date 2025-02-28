from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response

from open_producten.producttypen.models import ProductType, Thema
from open_producten.producttypen.serializers import ThemaSerializer
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet


class ThemaFilterSet(FilterSet):

    class Meta:
        model = Thema
        fields = {
            "gepubliceerd": ["exact"],
            "naam": ["exact"],
            "hoofd_thema__naam": ["exact"],
            "hoofd_thema__id": ["exact"],
            "aanmaak_datum": ["exact", "gte", "lte"],
            "update_datum": ["exact", "gte", "lte"],
        }


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
    filterset_class = ThemaFilterSet

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
