from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel


class TagType(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        help_text=_("Name of the tag type"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Tag type")
        verbose_name_plural = _("Tag types")

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=100, help_text=_("Name of the tag")
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        null=True,
        blank=True,
        help_text=_("Icon of the tag"),
    )
    type = models.ForeignKey(
        TagType,
        null=True,
        blank=True,
        verbose_name=_("Type"),
        on_delete=models.SET_NULL,
        related_name="tags",
        help_text=_("The related tag type"),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
