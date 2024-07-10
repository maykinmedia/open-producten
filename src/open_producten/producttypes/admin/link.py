from django.contrib import admin

from ..models import Link


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1
    ordering = ("pk",)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("product_type", "name", "url")
