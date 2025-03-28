from django.contrib import admin

from ..models import Link


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1
    ordering = ("pk",)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("producttype", "naam", "url")
    list_filter = ("producttype__code",)
    search_fields = ("naam", "producttype__translations__naam")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("producttype")
