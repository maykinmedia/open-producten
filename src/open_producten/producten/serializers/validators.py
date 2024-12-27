from django.core.exceptions import ValidationError

from rest_framework import serializers

from open_producten.producten.models.product import validate_bsn_or_kvk
from open_producten.utils.serializers import get_from_serializer_data_or_instance


class BsnOrKvkValidator:
    requires_context = True

    def __call__(self, value, serializer):
        bsn = get_from_serializer_data_or_instance("bsn", value, serializer)
        kvk = get_from_serializer_data_or_instance("kvk", value, serializer)
        try:
            validate_bsn_or_kvk(bsn, kvk)
        except ValidationError as e:
            raise serializers.ValidationError({"bsn_or_kvk": e.message})
