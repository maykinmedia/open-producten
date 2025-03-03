from django.core.validators import RegexValidator

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_basic_type


class SimplifyCharFieldWithRegex(OpenApiSerializerFieldExtension):
    """
    DRF Spectacular extension to replace CharField with RegexValidator
    so that it appears as a simple "string" instead of showing regex patterns.
    """

    target_class = "rest_framework.serializers.CharField"  # Applies to CharField

    def map_serializer_field(self, auto_schema, direction):
        field = self.target  # Get the CharField instance

        # Check if any validator is a RegexValidator
        if any(isinstance(validator, RegexValidator) for validator in field.validators):
            return build_basic_type(str)

        return build_basic_type(str)
