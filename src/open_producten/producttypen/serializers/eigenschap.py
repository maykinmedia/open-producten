from rest_framework import serializers

from open_producten.producttypen.models import Eigenschap


class EigenschapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eigenschap
        fields = ["naam", "waarde"]
