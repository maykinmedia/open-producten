from rest_framework import serializers

from open_producten.producttypes.models import Category, ProductType

from .children import QuestionSerializer, UpnSerializer


class SimpleProductTypeSerializer(serializers.ModelSerializer):
    uniform_product_name = UpnSerializer()

    class Meta:
        model = ProductType
        exclude = ("id", "categories", "conditions", "tags", "related_product_types")


class CategorySerializer(serializers.ModelSerializer):
    product_types = SimpleProductTypeSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Category
        exclude = ("id", "path", "depth", "numchild")
