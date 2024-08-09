from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class BasePublishableModel(BaseModel):
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=False,
        help_text=_("Whether the object is accessible through the API."),
    )
    created_on = models.DateTimeField(
        verbose_name=_("Created on"),
        auto_now_add=True,
        help_text=_("The datetime at which the object was created."),
    )
    updated_on = models.DateTimeField(
        verbose_name=_("Updated on"),
        auto_now=True,
        help_text=_("The datetime at which the object was last changed."),
    )

    class Meta:
        abstract = True
