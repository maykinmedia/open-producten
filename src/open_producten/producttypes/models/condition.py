from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce import models as tinymce_models

from open_producten.utils.models import BaseModel


class Condition(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        help_text=_("Short name of the condition"),
    )
    question = tinymce_models.HTMLField(
        verbose_name=_("Question"),
        help_text=_("Question used in the question-answer game"),
    )
    positive_text = tinymce_models.HTMLField(
        verbose_name=_("Positive text"),
        help_text=_("Description how to meet the condition"),
    )
    negative_text = tinymce_models.HTMLField(
        verbose_name=_("Negative text"),
        help_text=_("Description how not to meet the condition"),
    )

    class Meta:
        verbose_name = _("Condition")
        verbose_name_plural = _("Conditions")

    def __str__(self):
        return self.name
