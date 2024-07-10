from django.contrib import admin

from ..models import UniformProductName


@admin.register(UniformProductName)
class UniformProductNameAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
