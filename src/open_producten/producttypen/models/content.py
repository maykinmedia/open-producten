from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel


class ContentLabel(BaseModel):
    naam = models.CharField(max_length=100)


class ContentElement(BaseModel):
    label = models.ForeignKey(
        ContentLabel,
        verbose_name=_("label"),
        on_delete=models.PROTECT,
        help_text=_("Het label van dit content element"),
    )
    product_type = models.ForeignKey(
        "ProductType",
        verbose_name=_("label"),
        on_delete=models.CASCADE,
        help_text=_("Het product type van dit content element"),
        related_name="content_elementen",
    )
    toelichting = models.TextField(
        _("toelichting"),
        null=True,
        blank=True,
        help_text=_("De toelichting van dit content element"),
    )

    class Meta:
        verbose_name = _("content element")
        verbose_name_plural = _("content elementen")


class ContentElementTekst(BaseModel):
    taalcode = models.CharField(
        _("taalcode"),
        max_length=2,
        help_text=_("De taalcode van de content element tekst"),
    )
    content_element = models.ForeignKey(
        ContentElement,
        verbose_name=_("content element"),
        on_delete=models.CASCADE,
        help_text=_("Het content element van de content element tekst"),
        related_name="teksten",
    )

    class Meta:
        verbose_name = _("content element tekst")
        verbose_name_plural = _("content element teksten")
