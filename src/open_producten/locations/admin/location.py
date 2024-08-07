from django.contrib import admin

from ..models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "postcode", "street", "house_number")
    list_filter = ("city",)
    search_fields = ("name", "city")
