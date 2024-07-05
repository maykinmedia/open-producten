from django.db import models
from django.utils.translation import gettext_lazy as _

from .producttype import ProductType


class Link(models.Model):
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        related_name="links",
        on_delete=models.CASCADE,
        help_text=_("Related product type"),
    )
    name = models.CharField(
        verbose_name=_("Name"), max_length=100, help_text=_("Name for the link")
    )
    url = models.URLField(verbose_name=_("Url"), help_text=_("Url of the link"))

    class Meta:
        verbose_name = _("Product type link")
        verbose_name_plural = _("Product type links")

    def __str__(self):
        return f"{self.product_type}: {self.name}"
