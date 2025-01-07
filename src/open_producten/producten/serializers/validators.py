from django.core.exceptions import ValidationError

from rest_framework import serializers

from open_producten.producten.models.product import (
    validate_bsn_or_kvk,
    validate_dates,
    validate_status,
    validate_verbruiksobject,
)
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


class StatusValidator:
    requires_context = True

    def __call__(self, value, serializer):
        status = get_from_serializer_data_or_instance("status", value, serializer)
        product_type = get_from_serializer_data_or_instance(
            "product_type", value, serializer
        )
        try:
            validate_status(status, product_type)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class DateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        start_datum = get_from_serializer_data_or_instance(
            "start_datum", value, serializer
        )
        eind_datum = get_from_serializer_data_or_instance(
            "eind_datum", value, serializer
        )
        product_type = get_from_serializer_data_or_instance(
            "product_type", value, serializer
        )
        try:
            validate_dates(start_datum, eind_datum, product_type)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class VerbruiksObjectValidator:
    requires_context = True

    def __call__(self, value, serializer):
        verbruiksobject = get_from_serializer_data_or_instance(
            "verbruiksobject", value, serializer
        )
        product_type = get_from_serializer_data_or_instance(
            "product_type", value, serializer
        )
        try:
            validate_verbruiksobject(verbruiksobject, product_type)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
