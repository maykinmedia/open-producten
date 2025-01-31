from django.core.exceptions import ValidationError

from rest_framework import serializers
from rest_framework.serializers import Serializer

from open_producten.producten.models.product import (
    validate_bsn_or_kvk,
    validate_dates,
    validate_eind_datum,
    validate_start_datum,
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


def get_from_serializer_data_or_instance_and_changed(
    field: str, data: dict, serializer: Serializer
):
    value = get_from_serializer_data_or_instance(field, data, serializer)
    changed = data.get(field) is not None and (
        serializer.instance is None
        or data.get(field) != getattr(serializer.instance, field)
    )
    return value, changed


class StatusValidator:
    requires_context = True

    def __call__(self, value, serializer):
        status, status_changed = get_from_serializer_data_or_instance_and_changed(
            "status", value, serializer
        )
        product_type, product_type_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "product_type", value, serializer
            )
        )

        try:
            if status_changed or product_type_changed:
                validate_status(status, product_type)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class DateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        start_datum, start_datum_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "start_datum", value, serializer
            )
        )
        eind_datum, eind_datum_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "eind_datum", value, serializer
            )
        )
        product_type, product_type_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "product_type", value, serializer
            )
        )
        try:
            if start_datum_changed or product_type_changed:
                validate_start_datum(start_datum, product_type)
            if eind_datum_changed or product_type_changed:
                validate_eind_datum(eind_datum, product_type)
            validate_dates(start_datum, eind_datum)
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
