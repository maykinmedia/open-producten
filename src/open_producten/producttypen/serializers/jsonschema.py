from django_json_schema.models import JsonSchema
from rest_framework import serializers


class JsonSchemaSerializer(serializers.ModelSerializer):

    schema = serializers.DictField()

    class Meta:
        model = JsonSchema
        fields = "__all__"
