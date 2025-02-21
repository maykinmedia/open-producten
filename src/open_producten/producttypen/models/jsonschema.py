from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from jsonschema import Draft202012Validator, validate
from jsonschema.exceptions import (
    SchemaError,
    ValidationError as JsonSchemaValidationError,
)


class JsonSchema(models.Model):
    naam = models.CharField(
        _("naam"), help_text=_("Naam van het json schema."), max_length=200, unique=True
    )

    schema = models.JSONField(
        _("schema"), help_text=_("Het schema waartegen gevalideerd kan worden.")
    )

    class Meta:
        verbose_name = _("Json schema")
        verbose_name_plural = _("Json Schemas")

    def __str__(self):
        return self.naam

    def clean(self):
        try:
            Draft202012Validator.check_schema(self.schema)
        except SchemaError as e:
            raise ValidationError(e.message)

    def validate(self, json: dict) -> None:
        try:
            validate(json, self.schema, cls=Draft202012Validator)
        except JsonSchemaValidationError as e:
            raise ValidationError(e.message)  # TODO
