from datetime import date

from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet as _FilterSet
from rest_framework import serializers


class FilterSet(_FilterSet):
    """
    Add help texts for model field filters
    """

    @classmethod
    def filter_for_field(cls, field, field_name, lookup_expr=None):
        filter = super().filter_for_field(field, field_name, lookup_expr)

        if not filter.extra.get("help_text"):
            filter.extra["help_text"] = getattr(field, "help_text", None)
        return filter


class FilterBackend(DjangoFilterBackend):
    filterset_base = FilterSet


class CharArrayFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ChoiceArrayFilter(django_filters.BaseInFilter, django_filters.ChoiceFilter):
    pass


class ManyWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        if name not in data:
            return []

        return data.getlist(name)


class ManyCharField(forms.CharField):
    widget = ManyWidget

    def to_python(self, value):
        if not value:
            return []

        return value


class ManyCharFilter(django_filters.CharFilter):
    # django-filter doesn't support several uses of the same query param out of the box
    # so we need to do it ourselves
    field_class = ManyCharField


class ManyRegexValidator(RegexValidator):

    def __call__(self, values):
        for value in values:
            super().__call__(value)


class TranslationFilter(django_filters.CharFilter):
    """

    Simplifies Django-parler field translations.

    ProductType.naam -> translations__naam
    Product.product_type.naam -> product_type__translations__naam
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "__" in self.field_name:
            field_names = self.field_name.split("__")
            assert len(field_names) == 2

            self.model_field_name = field_names[0]
            self.field_name = field_names[1]

        else:
            self.model_field_name = None

    def filter(self, qs, value):

        if value in django_filters.constants.EMPTY_VALUES:
            return qs

        lookup = "translations__%s__%s" % (self.field_name, self.lookup_expr)
        language_lookup = "translations__language_code"

        if self.model_field_name:
            lookup = f"{self.model_field_name}__{lookup}"
            language_lookup = f"{self.model_field_name}__{language_lookup}"

        language_code = self.parent.request.LANGUAGE_CODE

        qs = self.get_method(qs)(**{lookup: value, language_lookup: language_code})
        return qs


class Operators(models.TextChoices):
    exact = "exact", _("gelijk aan")
    gt = "gt", _("grooter dan")
    gte = "gte", _("grooter dan of gelijk aan")
    lt = "lt", _("kleiner dan")
    lte = "lte", _("kleiner dan of gelijk aan")
    icontains = "icontains", _("case-insensitive partial match")
    in_list = "in", _("in een lijst van waarden gescheiden door `|`")


def validate_data_attr_value_part(value_part: str, code: str):
    try:
        variable, operator, val = value_part.rsplit("__", 2)
    except ValueError:
        message = _(
            "Filter '%(value_part)s' heeft niet de format 'key__operator__waarde'"
        ) % {"value_part": value_part}
        raise serializers.ValidationError(message, code=code)

    if operator not in Operators.values:
        message = _("operator `%(operator)s` is niet bekend/ondersteund") % {
            "operator": operator
        }
        raise serializers.ValidationError(message, code=code)

    if operator not in (
        Operators.exact,
        Operators.icontains,
        Operators.in_list,
    ) and isinstance(string_to_value(val), str):
        message = _(
            "Operator `%(operator)s` ondersteund alleen datums and/or numerieke waarden"
        ) % {"operator": operator}
        raise serializers.ValidationError(message, code=code)


def validate_data_attr(value: list):
    code = "invalid-data-attr-query"

    for value_part in value:
        # check that comma can be only in the value part
        if "," in value_part.rsplit("__", 1)[0]:
            message = _(
                "Filter '%(value_part)s' moet de format 'key__operator__value' hebben, "
                "komma's kunnen alleen in de `waarde` worden toegevoegd"
            ) % {"value_part": value_part}
            raise serializers.ValidationError(message, code=code)

        validate_data_attr_value_part(value_part, code)


def string_to_value(value: str) -> str | float | date:
    if is_number(value):
        return float(value)
    elif is_date(value):
        return date.fromisoformat(value)

    return value


def is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False

    return True


def is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False

    return True


def filter_data_attr_value_part(
    value_part: str, field_name: str, queryset: models.QuerySet
) -> models.QuerySet:
    """
    filter one value part for data_attr filters
    """
    variable, operator, str_value = value_part.rsplit("__", 2)
    real_value = string_to_value(str_value)

    if operator == "exact":
        #  for exact operator try to filter on string and numeric values
        in_vals = [str_value]
        if real_value != str_value:
            in_vals.append(real_value)
        queryset = queryset.filter(**{f"{field_name}__{variable}__in": in_vals})
    elif operator == "icontains":
        # icontains treats everything like strings
        queryset = queryset.filter(
            **{f"{field_name}__{variable}__icontains": str_value}
        )
    elif operator == "in":
        # in must be a list
        values = str_value.split("|")
        queryset = queryset.filter(
            **{
                f"{field_name}__{variable}__in": [
                    string_to_value(value) for value in values
                ]
            }
        )

    else:
        # gt, gte, lt, lte operators
        queryset = queryset.filter(
            **{f"{field_name}__{variable}__{operator}": real_value}
        )
    return queryset
