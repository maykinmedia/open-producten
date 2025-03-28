import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet as _FilterSet


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


class TranslationFilter(django_filters.CharFilter):
    """

    Simplifies Django-parler field translations.

    ProductType.naam -> translations__naam
    Product.producttype.naam -> producttype__translations__naam
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
