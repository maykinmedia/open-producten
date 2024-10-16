from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce import models as tinymce_models

from open_producten.utils.models import BaseModel

from .category import Category
from .producttype import ProductType


class Question(BaseModel):
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="questions",
    )
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="questions",
    )
    question = models.CharField(verbose_name=_("Question"), max_length=250)
    answer = tinymce_models.HTMLField(verbose_name=_("Answer"))

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def clean(self):
        if self.category and self.product_type:
            raise ValidationError(
                "A question cannot have both a category and a product type"
            )

        if not self.category and not self.product_type:
            raise ValidationError(
                "A question must have either a category or a product type"
            )

    def __str__(self):
        return self.question
