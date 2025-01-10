from django_json_schema.models import JsonSchema
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from rest_framework import serializers


class JsonSchemaSerializer(serializers.ModelSerializer):

    schema = serializers.DictField()

    def validate_schema(self, schema):
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as e:
            raise serializers.ValidationError(e.message)

        return schema

    class Meta:
        model = JsonSchema
        fields = "__all__"
