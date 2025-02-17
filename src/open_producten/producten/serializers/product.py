from rest_framework import serializers

from open_producten.producten.models import Product
from open_producten.producten.serializers.validators import (
    BsnOrKvkValidator,
    DateValidator,
    StatusValidator,
)
from open_producten.producttypen.models import ProductType
from open_producten.producttypen.serializers.thema import NestedProductTypeSerializer


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="product-detail")
    product_type = NestedProductTypeSerializer(read_only=True)
    product_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), source="product_type"
    )

    class Meta:
        model = Product
        fields = "__all__"
        validators = [BsnOrKvkValidator(), DateValidator(), StatusValidator()]
