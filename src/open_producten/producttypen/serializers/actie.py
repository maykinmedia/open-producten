from rest_framework import serializers

from open_producten.producttypen.models import Actie, ProductType
from open_producten.producttypen.models.dmn_config import DmnConfig


class ActieSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    url = serializers.ReadOnlyField(source="url")

    tabel_endpoint = serializers.SlugRelatedField(
        slug_field="tabel_endpoint",
        queryset=DmnConfig.objects.all(),
        source="dmn_config",
    )

    url = serializers.ReadOnlyField()

    class Meta:
        model = Actie
        fields = ("id", "naam", "tabel_endpoint", "dmn_tabel_id", "url", "product_type_id")

    def create(self, validated_data):

        url = validated_data.pop("url").rsplit("/", 1)

        dmn_tabel_id = url.pop()

        super().create(validated_data)

    def update(self, instance, validated_data):

        super().update(instance, validated_data)


class NestedActieSerializer(ActieSerializer):
    class Meta:
        model = Actie
        fields = ("id", "naam", "url")
