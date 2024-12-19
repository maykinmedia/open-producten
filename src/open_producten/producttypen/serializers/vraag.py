from rest_framework import serializers

from open_producten.producttypen.models import Onderwerp, ProductType, Vraag
from open_producten.producttypen.serializers.validators import (
    ProductTypeOrOnderwerpValidator,
)


class VraagSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all(), required=False
    )
    onderwerp_id = serializers.PrimaryKeyRelatedField(
        source="onderwerp", queryset=Onderwerp.objects.all(), required=False
    )

    class Meta:
        model = Vraag
        fields = ("id", "product_type_id", "onderwerp_id", "vraag", "antwoord")
        validators = [ProductTypeOrOnderwerpValidator()]
