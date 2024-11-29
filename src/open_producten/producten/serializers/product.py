from django.core.validators import ValidationError

from rest_framework import serializers

from open_producten.producten.models import Product
from open_producten.producttypen.models import ProductType
from open_producten.producttypen.serializers.onderwerp import (
    SimpleProductTypeSerializer,
)
from open_producten.utils.serializers import model_to_dict_with_related_ids


class BaseProductSerializer(serializers.ModelSerializer):
    def validate(self, attrs):

        if self.partial:
            all_attrs = model_to_dict_with_related_ids(self.instance) | attrs
        else:
            all_attrs = attrs

        instance = Product(**all_attrs)

        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError({"bsn_or_kvk": e.message})

        return attrs


class ProductSerializer(BaseProductSerializer):
    product_type = SimpleProductTypeSerializer(read_only=True)
    product_type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all(), source="product_type"
    )

    class Meta:
        model = Product
        fields = "__all__"


class ProductUpdateSerializer(BaseProductSerializer):
    class Meta:
        model = Product
        exclude = ("product_type",)
