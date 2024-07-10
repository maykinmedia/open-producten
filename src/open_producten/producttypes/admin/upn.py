from django.contrib import admin

from ..models import Upn


@admin.register(Upn)
class UpnAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
