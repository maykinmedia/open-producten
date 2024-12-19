from uuid import UUID

from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from .models import BaseModel


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
