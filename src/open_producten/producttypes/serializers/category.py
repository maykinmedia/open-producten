from rest_framework import serializers

from open_producten.producttypes.models import Category, ProductType
from .children import QuestionSerializer, UpnSerializer


class SimpleProductTypeSerializer(serializers.ModelSerializer):
    uniform_product_name = UpnSerializer()

    class Meta:
        model = ProductType
        exclude = ("id", "categories", "conditions", "tags", "related_product_types")


class CategorySerializer(serializers.ModelSerializer):
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        write_only=True,
    )
    product_types = SimpleProductTypeSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    product_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        default=[],
        write_only=True,
    )

    class Meta:
        model = Category
        exclude = ("path", "depth", "numchild")

    def create(self, validated_data):
        product_types = validated_data.pop("product_type_ids")
        parent_category = validated_data.pop("parent_category")

        if parent_category:
            category = parent_category.add_child(**validated_data)
        else:
            category = Category.add_root(**validated_data)

        category.product_types.set(product_types)
        category.save()

        return category

    def update(self, instance, validated_data):
        product_types = validated_data.pop("product_type_ids")
        parent_category = validated_data.pop("parent_category")

        instance_parent = instance.get_parent()

        if parent_category is None and instance_parent is not None:
            last_root = Category.get_last_root_node()
            instance.move(last_root, "last-sibling")

        elif parent_category != instance_parent:
            instance.move(parent_category, "last-child")

        instance.refresh_from_db()

        instance = super().update(instance, validated_data)
        instance.product_types.set(product_types)
        instance.save()

        return instance
