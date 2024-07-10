from django.contrib import admin

from ..models import Field


class FieldInline(admin.TabularInline):
    model = Field
    extra = 1
