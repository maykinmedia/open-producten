from django_filters import rest_framework as filters


class FilterSet(filters.FilterSet):
    """
    Add help texts for model field filters
    """

    @classmethod
    def filter_for_field(cls, field, field_name, lookup_expr=None):
        filter = super().filter_for_field(field, field_name, lookup_expr)

        if not filter.extra.get("help_text"):
            filter.extra["help_text"] = getattr(field, "help_text", None)
        return filter


class FilterBackend(filters.DjangoFilterBackend):
    filterset_base = FilterSet
