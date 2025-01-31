from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BasePublishableModel


class Thema(BasePublishableModel):

    naam = models.CharField(
        verbose_name=_("naam"), max_length=255, help_text=_("Naam van het thema.")
    )

    hoofd_thema = models.ForeignKey(
        "self",
        verbose_name=_("hoofd thema"),
        help_text=_("Het hoofd thema van het thema."),
        related_name="sub_themas",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    beschrijving = models.TextField(
        verbose_name=_("beschrijving"),
        blank=True,
        default="",
        help_text=_("Beschrijving van het thema, ondersteund markdown format."),
    )

    class Meta:
        verbose_name = _("thema")
        verbose_name_plural = _("thema's")

    def __str__(self):
        return self.naam

    def clean(self):
        disallow_self_reference(self, self.hoofd_thema)

        validate_gepubliceerd_state(
            self.hoofd_thema, self.gepubliceerd, self.sub_themas
        )


def validate_gepubliceerd_state(hoofd_thema, gepubliceerd, sub_themas=None):
    if gepubliceerd and hoofd_thema and not hoofd_thema.gepubliceerd:
        raise ValidationError(
            _(
                "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
            )
        )

    if (
        not gepubliceerd
        and sub_themas
        and sub_themas.filter(gepubliceerd=True).exists()
    ):
        raise ValidationError(
            _(
                "Thema's kunnen niet ongepubliceerd worden als ze gepubliceerde sub-thema's hebben."
            )
        )


def disallow_self_reference(thema, hoofd_thema):
    if thema and hoofd_thema and thema.id == hoofd_thema.id:
        raise ValidationError("Een thema kan niet zijn eigen hoofd thema zijn.")
