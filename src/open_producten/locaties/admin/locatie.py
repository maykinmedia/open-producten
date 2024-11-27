from django.contrib.gis import admin

from open_producten.utils.geocode import GeoAdminMixin

from ..models import Locatie


@admin.register(Locatie)
class LocatieAdmin(GeoAdminMixin, admin.GISModelAdmin):
    list_display = ("naam", "stad", "postcode", "straat", "huisnummer")
    list_filter = ("stad",)
    search_fields = ("naam", "stad")
