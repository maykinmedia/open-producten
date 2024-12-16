from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from markdownx.models import MarkdownxField
from treebeard.exceptions import InvalidMoveToDescendant
from treebeard.mp_tree import MP_MoveHandler, MP_Node

from open_producten.utils.models import BasePublishableModel


class PublishedMoveHandler(MP_MoveHandler):
    def process(self):
        if self.pos == "sorted-child":
            hoofd_onderwerp = self.target
        else:  # sorted-sibling
            hoofd_onderwerp = self.target.hoofd_onderwerp

        if (
            self.node.gepubliceerd
            and hoofd_onderwerp
            and not hoofd_onderwerp.gepubliceerd
        ):
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
        help_text=_("Beschrijving van het onderwerp."),
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

    def clean_gepubliceerd_and_hoofd_onderwerp(
        self, gepubliceerd: bool, hoofd_onderwerp: Optional["Onderwerp"]
    ):
        """This cannot be called inside the normal clean method as the parent/hoofd_onderwerp will not be set yet."""
        if gepubliceerd and hoofd_onderwerp and not hoofd_onderwerp.gepubliceerd:
            raise ValidationError(
                _(
                    "Sub-onderwerpen kunnen niet zijn gepubliceerd als het hoofd-onderwerp dat niet is."
                )
            )
        if not gepubliceerd and self.get_children().filter(gepubliceerd=True).exists():
            raise ValidationError(
                _(
                    "Hoofd-onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben."
                )
            )
