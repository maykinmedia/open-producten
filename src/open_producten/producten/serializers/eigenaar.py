from rest_framework import serializers

from open_producten.producten.models import Eigenaar
from open_producten.producten.serializers.validators import (
    EigenaarIdentifierValidator,
    EigenaarVestigingsnummerValidator,
)


class EigenaarSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Eigenaar
        fields = ["id", "bsn_nummer", "kvk_nummer", "vestigingsnummer", "klantnummer"]
        validators = [
            EigenaarIdentifierValidator(),
            EigenaarVestigingsnummerValidator(),
        ]
