from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from markdownx.models import MarkdownxField

from open_producten.utils.models import BasePublishableModel


class Onderwerp(BasePublishableModel):

    naam = models.CharField(
        verbose_name=_("naam"), max_length=100, help_text=_("Naam van het onderwerp.")
    )

    hoofd_onderwerp = models.ForeignKey(
        "self",
        verbose_name=_("hoofd onderwerp"),
        help_text=_("Het hoofd onderwerp van het onderwerp."),
        related_name="sub_onderwerpen",
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
    )

    beschrijving = MarkdownxField(
        verbose_name=_("beschrijving"),
        blank=True,
        default="",
        help_text=_("Beschrijving van het onderwerp, ondersteund markdown format."),
    )

    class Meta:
        verbose_name = _("Onderwerp")
        verbose_name_plural = _("Onderwerpen")

    def __str__(self):
        return self.naam

    def clean(self):
        if (
            self.gepubliceerd
            and self.hoofd_onderwerp
            and not self.hoofd_onderwerp.gepubliceerd
        ):
            raise ValidationError(
                _(
                    "Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd."
                )
            )

        if (
            not self.gepubliceerd
            and self.sub_onderwerpen.filter(gepubliceerd=True).exists()
        ):
            raise ValidationError(
                _(
                    "Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben."
                )
            )
