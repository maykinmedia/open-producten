from rest_framework import serializers

from open_producten.producttypen.models import ExterneCode, ProductType


class NestedExterneCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExterneCode
        fields = ("naam", "code")


class ExterneCodeSerializer(serializers.ModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = ExterneCode
        fields = ["naam", "code", "product_type"]
