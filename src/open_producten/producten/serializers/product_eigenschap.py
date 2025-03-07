from rest_framework import serializers

from open_producten.producten.models import ProductEigenschap
from open_producten.producten.serializers.validators import ProductEigenschapValidator


class NestedProductEigenschapSerializer(serializers.ModelSerializer):
    naam = serializers.CharField()

    class Meta:
        model = ProductEigenschap
        fields = ["waarde", "naam"]


class ProductEigenschapSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductEigenschap
        fields = ["eigenschap", "product", "waarde"]
        validators = [ProductEigenschapValidator()]
