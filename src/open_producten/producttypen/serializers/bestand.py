from rest_framework import serializers

from open_producten.producttypen.models import Bestand, ProductType


# TODO does not have viewset
class BestandSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Bestand
        fields = ("id", "bestand", "product_type_id")
