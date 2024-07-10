from django.contrib import admin

from ..models import File


class FileInline(admin.TabularInline):
    model = File
    extra = 1


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("product_type", "file")
    list_filter = ("product_type",)
