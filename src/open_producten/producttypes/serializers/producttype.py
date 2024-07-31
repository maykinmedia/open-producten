from django.db import transaction

from rest_framework import serializers

from ..models import Category, Condition, ProductType, Tag, UniformProductName
from .children import (
    ConditionSerializer,
    FieldSerializer,
    LinkSerializer,
    PriceSerializer,
    QuestionSerializer,
    TagSerializer,
)


class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ("id", "path", "depth", "numchild")


class ProductTypeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), default=[], write_only=True
    )

    related_product_types = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ProductType.objects.all(), default=[]
    )

    uniform_product_name = serializers.PrimaryKeyRelatedField(
        queryset=UniformProductName.objects.all()
    )

    conditions = ConditionSerializer(many=True, read_only=True)
    condition_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Condition.objects.all(), default=[]
    )

    categories = SimpleCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Category.objects.all(),
        default=[],
    )

    questions = QuestionSerializer(many=True, read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    prices = PriceSerializer(many=True, read_only=True)
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = ProductType
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        uniform_product_name_id = validated_data.pop("uniform_product_name")

        related_product_types = validated_data.pop("related_product_types")
        categories = validated_data.pop("category_ids")
        conditions = validated_data.pop("condition_ids")
        tags = validated_data.pop("tag_ids")

        product_type = ProductType.objects.create(
            **validated_data, uniform_product_name=uniform_product_name_id
        )

        product_type.related_product_types.set(related_product_types)
        product_type.categories.set(categories)
        product_type.tags.set(tags)
        product_type.conditions.set(conditions)

        product_type.save()

        return product_type

    def update(self, instance, validated_data):
        related_product_types = validated_data.pop("related_product_types")
        categories = validated_data.pop("category_ids")
        conditions = validated_data.pop("condition_ids")
        tags = validated_data.pop("tag_ids")

        instance = super().update(instance, validated_data)

        instance.related_product_types.set(related_product_types)
        instance.categories.set(categories)
        instance.tags.set(tags)
        instance.conditions.set(conditions)

        instance.save()

        return instance
