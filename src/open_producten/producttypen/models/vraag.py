from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from markdownx.models import MarkdownxField

from open_producten.utils.models import BaseModel

from .producttype import ProductType
from .thema import Thema


class Vraag(BaseModel):
    thema = models.ForeignKey(
        Thema,
        verbose_name=_("thema"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="vragen",
        help_text=_("Het thema waarbij deze vraag hoort."),
    )
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("Product type"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="vragen",
        help_text=_("Het product type waarbij deze vraag hoort."),
    )
    vraag = models.CharField(
        verbose_name=_("vraag"),
        max_length=250,
        help_text=_("De vraag die wordt beantwoord."),
    )
    antwoord = MarkdownxField(
        verbose_name=_("antwoord"),
        help_text=_("Het antwoord op de vraag, ondersteund markdown format."),
    )

    class Meta:
        verbose_name = _("Vraag")
        verbose_name_plural = _("Vragen")

    def clean(self):
        validate_thema_or_product_type(self.thema, self.product_type)

    def __str__(self):
        return self.vraag


def validate_thema_or_product_type(thema, product_type):
    if thema and product_type:
        raise ValidationError(
            _("Een vraag kan niet gelink zijn aan een thema en een product type.")
        )

    if not thema and not product_type:
        raise ValidationError(
            _("Een vraag moet gelinkt zijn aan een thema of een product type.")
        )
