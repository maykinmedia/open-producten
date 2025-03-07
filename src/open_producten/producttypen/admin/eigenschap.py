from django.contrib import admin

from open_producten.producttypen.models import Eigenschap


class EigenschapInline(admin.TabularInline):
    model = Eigenschap
    extra = 1
    ordering = ("pk",)
