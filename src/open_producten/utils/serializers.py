from uuid import UUID

from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import BaseModel


def build_array_duplicates_error_message(objects: list, field: str, errors):
    object_set = set()
    errors_messages = []
    for idx, obj in enumerate(objects):
        if obj in object_set:
            errors_messages.append(
                _(
                    "Dubbel {} object id: {} op index {}.".format(
                        type(obj).__name__, obj.id, idx
                    )
                )
            )

        object_set.add(obj)

    if errors_messages:
        errors[field] = errors_messages


def model_to_dict_with_related_ids(model: BaseModel) -> dict:
    """Creates a dict from a model and appends UUID fields with '_id'"""
    model_dict = model_to_dict(model)

    for k, v in list(model_dict.items()):
        if isinstance(v, UUID):
            model_dict[f"{k}_id"] = model_dict.pop(k)

    return model_dict

# sets date example value to dd-mm-yyyy
@extend_schema_field(dict(example="01-12-2024", **build_basic_type(OpenApiTypes.DATE)))
class CustomDateField(serializers.DateField):
    pass


@extend_schema_field(
    dict(example="01-12-2024T20:30:30+0200", **build_basic_type(OpenApiTypes.DATE))
)
class CustomDateTimeField(serializers.DateTimeField):
    pass
