from django.contrib import admin

from open_producten.producttypen.models import ExterneCode


class ExterneCodeInline(admin.TabularInline):
    model = ExterneCode
    extra = 1
    ordering = ("pk",)
