from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from open_producten.producten.models import Eigenaar, Product
from open_producten.producten.serializers.eigenaar import EigenaarSerializer
from open_producten.producten.serializers.validators import (
    DataObjectValidator,
    DateValidator,
    StatusValidator,
    VerbruiksObjectValidator,
)
from open_producten.producttypen.models import ProductType
from open_producten.producttypen.serializers.thema import NestedProductTypeSerializer
from open_producten.utils.drf_validators import NestedObjectsValidator


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "product response",
            value={
                "id": "da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                "url": "https://gemeente.open-producten.nl/producten/api/v0/producten/da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                "start_datum": "2024-12-01",
                "eind_datum": "2026-12-01",
                "aanmaak_datum": "2019-08-24T14:15:22Z",
                "update_datum": "2019-08-24T14:15:22Z",
                "producttype": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "code": "129380-c21231",
                    "keywords": ["auto"],
                    "uniforme_product_naam": "parkeervergunning",
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": "2019-08-24T14:15:22Z",
                    "update_datum": "2019-08-24T14:15:22Z",
                },
                "gepubliceerd": False,
                "eigenaren": [
                    {
                        "id": "9de01697-7fc5-4113-803c-a8c9a8dad4f2",
                        "bsn": "111222333",
                    }
                ],
                "status": "gereed",
                "prijs": "20.20",
                "frequentie": "eenmalig",
                "verbruiksobject": {"uren": 130},
                "data": {"max_uren": 150},
            },
            response_only=True,
        ),
        OpenApiExample(
            "product request",
            value={
                "start_datum": "2024-12-01",
                "eind_datum": "2026-12-01",
                "producttype_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "gepubliceerd": False,
                "eigenaren": [
                    {"bsn": "111222333"},
                ],
                "status": "gereed",
                "prijs": "20.20",
                "frequentie": "eenmalig",
                "verbruiksobject": {"uren": 130},
            },
            media_type="multipart/form-data",
            request_only=True,
        ),
    ],
)
class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="product-detail")
    producttype = NestedProductTypeSerializer(read_only=True)
    producttype_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all(), source="producttype"
    )
    eigenaren = EigenaarSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"
        validators = [
            DateValidator(),
            StatusValidator(),
            VerbruiksObjectValidator(),
            DataObjectValidator(),
            NestedObjectsValidator("eigenaren", Eigenaar),
        ]

    def validate_eigenaren(self, eigenaren: list[Eigenaar]) -> list[Eigenaar]:
        if len(eigenaren) == 0:
            raise serializers.ValidationError(_("Er is minimaal één eigenaar vereist."))
        return eigenaren

    @transaction.atomic()
    def create(self, validated_data):
        eigenaren = validated_data.pop("eigenaren", [])

        product = super().create(validated_data)

        for eigenaar in eigenaren:
            eigenaar.pop("id", None)
            EigenaarSerializer().create(eigenaar | {"product": product})

        return product

    @transaction.atomic()
    def update(self, instance, validated_data):
        eigenaren = validated_data.pop("eigenaren", None)
        product = super().update(instance, validated_data)

        if eigenaren is not None:
            current_eigenaren_ids = set(product.eigenaren.values_list("id", flat=True))
            seen_eigenaren_ids = set()

            for eigenaar in eigenaren:
                eigenaar_id = eigenaar.pop("id", None)
                if eigenaar_id is None:
                    EigenaarSerializer().create(eigenaar | {"product": product})

                else:
                    existing_eigenaar = Eigenaar.objects.get(id=eigenaar_id)
                    EigenaarSerializer().update(existing_eigenaar, eigenaar)
                    seen_eigenaren_ids.add(eigenaar_id)

            product.eigenaren.filter(
                id__in=(current_eigenaren_ids - seen_eigenaren_ids)
            ).delete()

        return product
