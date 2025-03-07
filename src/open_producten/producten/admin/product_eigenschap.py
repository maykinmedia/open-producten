from django.contrib import admin

from open_producten.logging.admin_tools import AuditLogInlineformset
from open_producten.producten.models import ProductEigenschap


class ProductEigenschapInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = ProductEigenschap
    extra = 1
    ordering = ("pk",)
