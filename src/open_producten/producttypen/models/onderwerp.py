from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from markdownx.models import MarkdownxField
from treebeard.exceptions import InvalidMoveToDescendant
from treebeard.mp_tree import MP_MoveHandler, MP_Node

from open_producten.utils.models import BasePublishableModel


class PublishedMoveHandler(MP_MoveHandler):
    def process(self):
        if self.node.gepubliceerd and not self.target.gepubliceerd:
            raise InvalidMoveToDescendant(
                _(
                    "Gepubliceerde onderwerpen kunnen kunnen geen ongepubliceerd hoofd-onderwerp hebben."
                )
            )
        return super().process()


class Onderwerp(MP_Node, BasePublishableModel):
    node_order_by = ["naam"]

    naam = models.CharField(
        verbose_name=_("naam"), max_length=100, help_text=_("Naam van het onderwerp.")
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
        ordering = ("path",)

    def __str__(self):
        return self.naam

    @property
    def hoofd_onderwerp(self):
        return self.get_parent()

    def move(self, target, pos=None):
        return PublishedMoveHandler(self, target, pos).process()

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
            and self.get_children().filter(gepubliceerd=True).exists()
        ):
            raise ValidationError(
                _(
                    "Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben."
                )
            )
