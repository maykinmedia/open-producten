from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import serializers

from open_producten.producttypes.models import Category, ProductType, UniformProductName
from open_producten.utils.serializers import build_array_duplicates_error_message

from .children import QuestionSerializer


class SimpleProductTypeSerializer(serializers.ModelSerializer):
    uniform_product_name = serializers.SlugRelatedField(
        slug_field="uri", queryset=UniformProductName.objects.all()
    )

    class Meta:
        model = ProductType
        exclude = (
            "categories",
            "conditions",
            "tags",
            "related_product_types",
            "organisations",
            "locations",
            "contacts",
        )


class CategorySerializer(serializers.ModelSerializer):
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
    )
    product_types = SimpleProductTypeSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    product_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        default=[],
        write_only=True,
        source="product_types",
    )

    class Meta:
        model = Category
        exclude = ("path", "depth", "numchild")

    def _handle_relations(self, instance, product_types: list[ProductType]):
        errors = dict()
        if product_types is not None:
            build_array_duplicates_error_message(
                product_types, "product_type_ids", errors
            )
            instance.product_types.set(product_types)

        if errors:
            raise serializers.ValidationError(errors)

    def _validate_category(self, category):
        try:
            category.clean()
        except ValidationError as err:
            raise serializers.ValidationError({"parent_category": err.message})

    @transaction.atomic()
    def create(self, validated_data):
        product_types = validated_data.pop("product_types")
        parent_category = validated_data.pop("parent_category")

        if parent_category:
            category = parent_category.add_child(**validated_data)
        else:
            category = Category.add_root(**validated_data)

        self._validate_category(category)
        self._handle_relations(category, product_types)
        category.save()

        return category

    @transaction.atomic()
    def update(self, instance, validated_data):
        product_types = validated_data.pop("product_types", None)
        parent_category = validated_data.pop(
            "parent_category", "ignore"
        )  # None is a valid value

        if parent_category != "ignore":
            instance_parent = instance.get_parent()
            if parent_category is None and instance_parent is not None:
                last_root = Category.get_last_root_node()
                instance.move(last_root, "last-sibling")

            elif parent_category != instance_parent:
                instance.move(parent_category, "last-child")

            instance.refresh_from_db()

        instance = super().update(instance, validated_data)
        self._validate_category(instance)
        self._handle_relations(instance, product_types)
        instance.save()
        return instance
