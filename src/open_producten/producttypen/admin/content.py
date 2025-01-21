from django.contrib import admin

from ordered_model.admin import OrderedInlineMixin
from parler.admin import TranslatableTabularInline

from open_producten.producttypen.models import ContentElement, ContentLabel


@admin.register(ContentLabel)
class ContentLabelAdmin(admin.ModelAdmin):
    search_fields = ("naam",)


class ContentElementInline(OrderedInlineMixin, TranslatableTabularInline):
    model = ContentElement
    readonly_fields = ("move_up_down_links",)
    ordering = ("order",)
    autocomplete_fields = ("labels",)
    extra = 1
