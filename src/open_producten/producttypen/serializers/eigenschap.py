from rest_framework import serializers

from open_producten.producttypen.models import Eigenschap, ProductType


class NestedEigenschapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eigenschap
        fields = ["naam"]


class EigenschapSerializer(serializers.ModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = Eigenschap
        fields = ["naam", "product_type"]
