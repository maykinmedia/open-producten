from django.db import models
from django.utils.translation import gettext_lazy as _

from .location import BaseLocation


class OrganisationType(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        unique=True,
        help_text=_("Organisation type"),
    )

    class Meta:
        verbose_name = _("Organisation type")
        verbose_name_plural = _("Organisation types")

    def __str__(self):
        return self.name


class Neighbourhood(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        unique=True,
        help_text=_("Neighbourhood name"),
    )

    class Meta:
        verbose_name = _("Neighbourhood")
        verbose_name_plural = _("Neighbourhoods")

    def __str__(self):
        return self.name


class Organisation(BaseLocation):
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=100,
        unique=True,
        help_text=_("Slug of the organisation"),
    )
    logo = models.ImageField(
        verbose_name=_("Logo"),
        null=True,
        blank=True,
        help_text=_("Logo of the organisation"),
    )

    type = models.ForeignKey(
        OrganisationType,
        verbose_name=_("Type"),
        related_name="organisations",
        on_delete=models.CASCADE,
        help_text=_("Organisation type"),
    )

    neighbourhood = models.ForeignKey(
        Neighbourhood,
        verbose_name=_("Neighbourhood"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organisation",
        help_text=_("The neighbourhood of the organisation"),
    )

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")

    def __str__(self):
        return f"{self.name}"
