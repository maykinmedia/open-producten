from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import serializers

from open_producten.producttypen.models import (
    Onderwerp,
    ProductType,
    UniformeProductNaam,
)

from ...utils.drf_validators import DuplicateIdValidator
from .vraag import VraagSerializer


class SimpleProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="uri", queryset=UniformeProductNaam.objects.all()
    )

    class Meta:
        model = ProductType
        fields = (
            "id",
            "naam",
            "samenvatting",
            "beschrijving",
            "keywords",
            "uniforme_product_naam",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
        )


class OnderwerpSerializer(serializers.ModelSerializer):
    hoofd_onderwerp = serializers.PrimaryKeyRelatedField(
        queryset=Onderwerp.objects.all(),
        allow_null=True,
    )
    product_typen = SimpleProductTypeSerializer(many=True, read_only=True)
    vragen = VraagSerializer(many=True, read_only=True)

    product_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        write_only=True,
        source="product_typen",
    )

    class Meta:
        model = Onderwerp
        fields = (
            "id",
            "naam",
            "beschrijving",
            "vragen",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "hoofd_onderwerp",
            "product_typen",
            "product_type_ids",
        )
        validators = [DuplicateIdValidator(["product_type_ids"])]

    def _validate_onderwerp(self, onderwerp):
        try:
            onderwerp.clean()
        except ValidationError as err:
            raise serializers.ValidationError({"hoofd_onderwerp": err.message})

    @transaction.atomic()
    def create(self, validated_data):
        product_typen = validated_data.pop("product_typen")

        onderwerp = Onderwerp.objects.create(**validated_data)

        self._validate_onderwerp(onderwerp)
        onderwerp.product_typen.set(product_typen)
        onderwerp.save()

        return onderwerp

    @transaction.atomic()
    def update(self, instance, validated_data):
        product_typen = validated_data.pop("product_typen", None)
        hoofd_onderwerp = validated_data.pop(
            "hoofd_onderwerp", "ignore"
        )  # None is a valid value

        if hoofd_onderwerp != "ignore":
            instance.hoofd_onderwerp = hoofd_onderwerp

        instance = super().update(instance, validated_data)
        self._validate_onderwerp(instance)
        if product_typen:
            instance.product_typen.set(product_typen)
        instance.save()
        return instance
