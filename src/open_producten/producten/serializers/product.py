from django.db import transaction

from rest_framework import serializers

from open_producten.producten.models import Eigenaar, Product
from open_producten.producten.serializers.eigenaar import EigenaarSerializer
from open_producten.producten.serializers.validators import (
    DateValidator,
    StatusValidator,
)
from open_producten.producttypen.models import ProductType
from open_producten.producttypen.serializers.thema import NestedProductTypeSerializer
from open_producten.utils.drf_validators import NestedObjectsValidator


class ProductSerializer(serializers.ModelSerializer):
    product_type = NestedProductTypeSerializer(read_only=True)
    product_type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all(), source="product_type"
    )
    eigenaren = EigenaarSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"
        validators = [
            DateValidator(),
            StatusValidator(),
            NestedObjectsValidator("eigenaren", Eigenaar),
        ]

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

                    # serializer = EigenaarSerializer(existing_eigenaar, data=eigenaar, partial=self.partial)
                    # serializer.is_valid(raise_exception=True)
                    # serializer.save()

                    seen_eigenaren_ids.add(eigenaar_id)

            product.eigenaren.filter(
                id__in=(current_eigenaren_ids - seen_eigenaren_ids)
            ).delete()

        return product


# def update_nested_object(object_list: list[dict], child_serializer: Serializer):
#     ids = [obj["id"] for obj in object_list]
#     product.eigenaren.exclude(id__in=ids).delete()
#
#     for obj in object_list:
#         if obj_id := obj.pop("id", None):
#             existing_eigenaar = Eigenaar.objects.get(id=obj_id)
#             child_serializer().update(existing_eigenaar, obj)
#         else:
#             child_serializer().create(obj | {"product": product})
