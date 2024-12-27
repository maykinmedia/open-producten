from rest_framework import serializers

from open_producten.producttypen.models import ProductType, Thema, Vraag
from open_producten.producttypen.serializers.validators import (
    ProductTypeOrThemaValidator,
)


class VraagSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type",
        queryset=ProductType.objects.all(),
        required=False,
        allow_null=True,
    )
    thema_id = serializers.PrimaryKeyRelatedField(
        source="thema",
        queryset=Thema.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Vraag
        fields = ("id", "product_type_id", "thema_id", "vraag", "antwoord")
        validators = [ProductTypeOrThemaValidator()]


class NestedVraagSerializer(VraagSerializer):
    class Meta:
        model = Vraag
        fields = ("id", "vraag", "antwoord")
