from rest_framework import serializers

from open_producten.producttypen.models import ExterneCode


class ExterneCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExterneCode
        fields = ["systeem", "code"]
