from django import forms
from django.contrib import admin

from ordered_model.admin import OrderedModelAdmin

from ..models import Question


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"


@admin.register(Question)
class QuestionAdmin(OrderedModelAdmin):
    form = QuestionAdminForm
    list_filter = ("category",)
    list_display = (
        "question",
        "category",
        "product_type",
    )
    search_fields = (
        "question",
        "answer",
        "category__name",
        "product__name",
    )


class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionAdminForm
    extra = 1

    fields = [
        "question",
        "answer",
    ]
