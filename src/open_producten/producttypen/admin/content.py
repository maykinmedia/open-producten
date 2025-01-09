from django.contrib import admin

from open_producten.producttypen.models.content import ContentElement
from open_producten.producttypen.models.producttype import ProductTypeVertaling


class ContentElementInline(admin.TabularInline):
    model = ContentElement


class ProductTypeVertalingInline(admin.TabularInline):
    model = ProductTypeVertaling
