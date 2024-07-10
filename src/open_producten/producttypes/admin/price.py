from django.contrib import admin

from ..models import Price, PriceOption


class PriceOptionInline(admin.TabularInline):
    model = PriceOption
    extra = 1
    ordering = ("description",)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    model = Price
    inlines = [PriceOptionInline]
