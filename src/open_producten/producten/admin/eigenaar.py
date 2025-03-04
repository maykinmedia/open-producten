from django.contrib import admin

from open_producten.logging.admin_tools import AuditLogInlineformset
from open_producten.producten.models import Eigenaar


class EigenaarInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Eigenaar
    extra = 1
