from django.contrib import admin

from open_producten.producttypen.models import Parameter


class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 1
    ordering = ("pk",)
