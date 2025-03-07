from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from open_producten.producttypen.models import ProductType, Thema, UniformeProductNaam

from ...utils.drf_validators import DuplicateIdValidator
from .validators import ThemaGepubliceerdStateValidator, ThemaSelfReferenceValidator


class NestedProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="naam", queryset=UniformeProductNaam.objects.all()
    )

    class Meta:
        model = ProductType
        fields = (
            "id",
            "code",
            "keywords",
            "uniforme_product_naam",
            "toegestane_statussen",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
        )


class ThemaSerializer(serializers.ModelSerializer):
    hoofd_thema = serializers.PrimaryKeyRelatedField(
        queryset=Thema.objects.all(),
        allow_null=True,
        help_text=_("Het hoofd thema waaronder dit thema valt."),
    )
    product_typen = NestedProductTypeSerializer(many=True, read_only=True)

    # TODO: remove?
    product_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        write_only=True,
        source="product_typen",
    )

    class Meta:
        model = Thema
        fields = (
            "id",
            "naam",
            "beschrijving",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "hoofd_thema",
            "product_typen",
            "product_type_ids",
        )
        validators = [
            DuplicateIdValidator(["product_type_ids"]),
            ThemaGepubliceerdStateValidator(),
            ThemaSelfReferenceValidator(),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        product_typen = validated_data.pop("product_typen")

        thema = Thema.objects.create(**validated_data)
        thema.product_typen.set(product_typen)

        return thema

    @transaction.atomic()
    def update(self, instance, validated_data):
        product_typen = validated_data.pop("product_typen", None)
        hoofd_thema = validated_data.pop(
            "hoofd_thema", "ignore"
        )  # None is a valid value

        if hoofd_thema != "ignore":
            instance.hoofd_thema = hoofd_thema

        instance = super().update(instance, validated_data)

        if product_typen:
            instance.product_typen.set(product_typen)

        return instance
