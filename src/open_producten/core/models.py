from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=False,
        help_text=_("Whether the object is accessible with the api."),
    )
    created_on = models.DateTimeField(
        verbose_name=_("Created on"),
        auto_now_add=True,
        help_text=_(
            "The date the object was created. This field is automatically set."
        ),
    )
    updated_on = models.DateTimeField(
        verbose_name=_("Updated on"),
        auto_now=True,
        help_text=_(
            "The date when the object was last changed. This field is automatically set."
        ),
    )

    class Meta:
        abstract = True
