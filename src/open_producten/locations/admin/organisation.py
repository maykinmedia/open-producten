from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import Neighbourhood, Organisation, OrganisationType


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    # List
    list_display = ("name", "type")
    list_filter = ("type__name", "city")
    search_fields = ("name",)
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    # Detail
    fieldsets = (
        (
            None,
            {"fields": ("published", "name", "slug", "type", "logo", "neighbourhood")},
        ),
        (_("Contact"), {"fields": ("email", "phone_number")}),
        (
            _("Address"),
            {"fields": ("street", "house_number", "postcode", "city")},
        ),
    )


@admin.register(OrganisationType)
class OrganisationTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Neighbourhood)
class NeighbourhoodAmin(admin.ModelAdmin):
    list_display = ("name",)
