from django.core.exceptions import ValidationError

from rest_framework import serializers

from ...utils.serializers import get_from_serializer_data_or_instance
from ..models.thema import disallow_self_reference, validate_gepubliceerd_state


class ThemaGepubliceerdStateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        hoofd_thema = get_from_serializer_data_or_instance(
            "hoofd_thema", value, serializer
        )
        gepubliceerd = get_from_serializer_data_or_instance(
            "gepubliceerd", value, serializer
        )
        sub_themas = serializer.instance.sub_themas if serializer.instance else None

        try:
            validate_gepubliceerd_state(hoofd_thema, gepubliceerd, sub_themas)
        except ValidationError as e:
            raise serializers.ValidationError({"hoofd_thema": e.message})


class ThemaSelfReferenceValidator:
    requires_context = True

    def __call__(self, value, serializer):
        thema = serializer.instance
        hoofd_thema = get_from_serializer_data_or_instance(
            "hoofd_thema", value, serializer
        )

        try:
            disallow_self_reference(thema, hoofd_thema)
        except ValidationError as e:
            raise serializers.ValidationError({"hoofd_thema": e.message})
