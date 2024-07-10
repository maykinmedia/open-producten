from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .category import Category
from .producttype import ProductType


class Question(models.Model):
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    question = models.CharField(verbose_name=_("Question"), max_length=250)
    answer = models.TextField(verbose_name=_("Answer"))

    order_with_respect_to = "category"

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def clean(self):
        if self.category and self.product:
            raise ValidationError(
                "A question cannot have both a category and a product"
            )

        if not self.category and not self.product:
            raise ValidationError("A question must have either a category or a product")

    def __str__(self):
        return self.question
