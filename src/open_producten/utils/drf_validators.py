from rest_framework import serializers

from open_producten.utils.serializers import clean_duplicate_ids_in_list


class DuplicateIdValidator:
    requires_context = True

    def __init__(self, fields: list[str]):
        self.fields = fields

    def __call__(self, value, serializer):
        errors = dict()
        for field in self.fields:
            if serializer.initial_data.get(field):
                clean_duplicate_ids_in_list(
                    serializer.initial_data[field], field, errors
                )

        if errors:
            raise serializers.ValidationError(errors)
