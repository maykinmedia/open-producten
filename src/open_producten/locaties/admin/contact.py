from django.contrib import admin

from ..models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("organisatie", "achternaam", "voornaam")
    list_filter = ("organisatie",)
    search_fields = ("voornaam", "achternaam")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("organisatie")
