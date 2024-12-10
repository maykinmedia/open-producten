from uuid import UUID

from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from rest_framework.serializers import Serializer
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers

from .models import BaseModel


def get_from_serializer_data_or_instance(
    field: str, data: dict, serializer: Serializer
):
    if field in data:
        return data[field]

    if serializer.instance:
        return getattr(serializer.instance, field)


def clean_duplicate_ids_in_list(values: list, field: str, errors):
    value_set = set()
    errors_messages = []
    for idx, value in enumerate(values):
        if value in value_set:
            errors_messages.append(_("Dubbel id: {} op index {}.").format(value, idx))

        value_set.add(value)

    if errors_messages:
        errors[field] = errors_messages


def model_to_dict_with_related_ids(model: BaseModel) -> dict:
    """Creates a dict from a model and appends UUID fields with '_id'"""
    model_dict = model_to_dict(model)

    for k, v in list(model_dict.items()):
        if isinstance(v, UUID):
            model_dict[f"{k}_id"] = model_dict.pop(k)

    return model_dict
