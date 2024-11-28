from uuid import UUID

from django.forms.models import model_to_dict

from .models import BaseModel


def build_array_duplicates_error_message(objects: list, field: str, errors):
    object_set = set()
    errors_messages = []
    for idx, obj in enumerate(objects):
        if obj in object_set:
            errors_messages.append(
                f"Duplicate {type(obj).__name__} id: {obj.id} at index {idx}"
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
