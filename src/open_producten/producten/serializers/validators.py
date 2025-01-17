from django.core.exceptions import ValidationError

from rest_framework import serializers

from open_producten.producten.models.product import validate_bsn_or_kvk, validate_dates
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


class DateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        start_datum = get_from_serializer_data_or_instance(
            "start_datum", value, serializer
        )
        eind_datum = get_from_serializer_data_or_instance(
            "eind_datum", value, serializer
        )
        try:
            validate_dates(start_datum, eind_datum)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
