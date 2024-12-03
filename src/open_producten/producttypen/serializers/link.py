from rest_framework import serializers

from open_producten.producttypen.models import Link, ProductType


class LinkSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Link
        exclude = ("product_type",)
