import json
import re
from datetime import datetime
from json.decoder import JSONDecodeError

from django.core.exceptions import ValidationError

from open_producten.producttypes.models import FieldTypes


def validate_bsn(bsn):
    """
    Validates that a bsn number is 9 digits and runs the 11 check.
    """

    if not re.match(r"^[0-9]{9}$", bsn):
        raise ValidationError("A bsn number consists of 9 digits.")

    total = sum(int(num) * (9 - i) for i, num in enumerate(bsn[:8]))
    total += int(bsn[8]) * -1

    if total == 0 or total % 11 != 0:
        raise ValidationError("Invalid bsn number")


def validate_checkbox(data):
    if data != "true" and data != "false":
        raise ValidationError("Checkbox must be true or false")


def validate_datetime_format(data, _format, field_type):
    try:
        datetime.strptime(data, _format)
    except ValueError:
        raise ValidationError(f"{field_type} should use {_format} format")


def validate_regex(data, pattern, field_type):
    if not re.match(pattern, data):
        raise ValidationError(f"invalid {field_type}")


def load(data):
    try:
        data = json.loads(data)
    except JSONDecodeError:
        raise ValidationError("invalid json")
    return data


def validate_select_boxes(data, choices):
    data = load(data)
    for v in set(data.values()):
        if not isinstance(v, bool):
            raise ValidationError("select box values should be boolean")

    if sorted(data.keys()) != sorted(choices):
        raise ValidationError("select box keys do not match the field choices")


def choice_exists(data, choices):
    if data not in choices:
        raise ValidationError("value does not exist in the field choices")


def validate_radio(data, choices):
    choice_exists(data, choices)


def validate_select(data, choices):
    validate_regex(data, "^(.*,?)+$", FieldTypes.SELECT)

    for d in data.split(","):
        choice_exists(d, choices)
