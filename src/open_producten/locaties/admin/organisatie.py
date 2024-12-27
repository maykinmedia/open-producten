from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _

from ..models import Organisatie


@admin.register(Organisatie)
class OrganisatieAdmin(admin.ModelAdmin):
    list_display = ("naam",)
    list_filter = ("stad",)
    search_fields = ("naam",)
    ordering = ("naam",)

    fieldsets = (
        (
            None,
            {"fields": ("naam",)},
        ),
        (_("Contact"), {"fields": ("email", "telefoonnummer")}),
        (
            _("Address"),
            {"fields": ("straat", "huisnummer", "postcode", "stad")},
        ),
    )
