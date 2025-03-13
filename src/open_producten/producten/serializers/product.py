from django.db import transaction
from django.utils.translation import gettext_lazy as _

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


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="product-detail")
    product_type = NestedProductTypeSerializer(read_only=True)
    product_type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all(), source="product_type"
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
