from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin
from ordered_model.admin import OrderedModelAdmin

from ..models import Vraag


@admin.register(Vraag)
class VraagAdmin(OrderedModelAdmin, MarkdownxModelAdmin):
    list_filter = ("onderwerp",)
    list_display = (
        "vraag",
        "onderwerp",
        "product_type",
    )
    search_fields = (
        "vraag",
        "antwoord",
        "onderwerp__naam",
        "product_type__naam",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("onderwerp", "product_type")


class VraagInline(admin.TabularInline):
    model = Vraag
    extra = 1

    fields = [
        "vraag",
        "antwoord",
    ]
