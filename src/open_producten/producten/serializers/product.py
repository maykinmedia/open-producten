from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from open_producten.producten.models import Product
from open_producten.producten.serializers.product_eigenschap import (
    NestedProductEigenschapSerializer,
    ProductEigenschapSerializer,
)
from open_producten.producten.serializers.validators import (
    BsnOrKvkValidator,
    DateValidator,
    StatusValidator,
    VerbruiksObjectValidator,
)
from open_producten.producttypen.models import Eigenschap, ProductType
from open_producten.producttypen.serializers.thema import NestedProductTypeSerializer
from open_producten.utils.serializers import (
    set_nested_serializer,
    validate_key_value_model_keys,
)


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="product-detail")
    product_type = NestedProductTypeSerializer(read_only=True)
    product_type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all(), source="product_type"
    )

    eigenschappen = NestedProductEigenschapSerializer(many=True, required=False)

    def validate_eigenschappen(self, parameters: list[dict]):
        return validate_key_value_model_keys(
            parameters,
            "naam",
            _("Er bestaat al een eigenschap met de naam {} voor dit Product."),
        )

    class Meta:
        model = Product
        fields = "__all__"
        validators = [
            BsnOrKvkValidator(),
            DateValidator(),
            StatusValidator(),
            VerbruiksObjectValidator(),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        eigenschappen = validated_data.pop("eigenschappen", [])

        product = super().create(validated_data)

        set_nested_serializer(
            [
                product_eigenschap
                | {
                    "product": product.id,
                    "eigenschap": self._get_eigenschap(
                        product_eigenschap.pop("naam"), product.product_type
                    ).id,
                }
                for product_eigenschap in eigenschappen
            ],
            ProductEigenschapSerializer,
        )

        return product

    def _get_eigenschap(self, naam, product_type):
        try:
            return product_type.eigenschappen.get(naam=naam)
        except Eigenschap.DoesNotExist:
            raise NotFound(
                _("Producttype {} heeft geen eigenschap `{}`").format(
                    product_type.id, naam
                )
            )

    @transaction.atomic()
    def update(self, instance, validated_data):
        eigenschappen = validated_data.pop("eigenschappen", None)

        instance = super().update(instance, validated_data)

        if eigenschappen is not None:
            instance.eigenschappen.all().delete()
            set_nested_serializer(
                [
                    product_eigenschap
                    | {
                        "product": instance.id,
                        "eigenschap": self._get_eigenschap(
                            product_eigenschap.pop("naam"), instance.product_type
                        ).id,
                    }
                    for product_eigenschap in eigenschappen
                ],
                ProductEigenschapSerializer,
            )

        return instance
