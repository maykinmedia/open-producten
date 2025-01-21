from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin
from ordered_model.admin import OrderedModelAdmin

from ..models import Vraag


@admin.register(Vraag)
class VraagAdmin(OrderedModelAdmin, MarkdownxModelAdmin):
    list_filter = ("thema",)
    list_display = (
        "vraag",
        "thema",
        "product_type",
    )
    search_fields = (
        "vraag",
        "antwoord",
        "thema__naam",
        "product_type__translations__naam",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("thema", "product_type")


class VraagInline(admin.TabularInline):
    model = Vraag
    extra = 1

    fields = [
        "vraag",
        "antwoord",
    ]
