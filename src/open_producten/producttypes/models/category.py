from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from tinymce import models as tinymce_models
from treebeard.exceptions import InvalidMoveToDescendant
from treebeard.mp_tree import MP_MoveHandler, MP_Node

from open_producten.utils.models import BasePublishableModel


class PublishedMoveHandler(MP_MoveHandler):
    def process(self):
        if self.node.published and not self.target.published:
            raise InvalidMoveToDescendant(
                _("Published nodes cannot be nested under unpublished ones.")
            )
        return super().process()


class Category(MP_Node, BasePublishableModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=100, help_text=_("Name of the category")
    )

    description = tinymce_models.HTMLField(
        verbose_name=_("Description"),
        blank=True,
        default="",
        help_text=_("Description of the category"),
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        null=True,
        blank=True,
        help_text=_("Icon of the category"),
    )
    image = models.ImageField(
        verbose_name=_("Image"),
        null=True,
        blank=True,
        help_text=_("Image of the category"),
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ("path",)

    def __str__(self):
        return self.name

    @property
    def parent_category(self):
        return self.get_parent()

    def move(self, target, pos=None):
        return PublishedMoveHandler(self, target, pos).process()

    def clean(self):
        if self.published and self.parent_category:
            if not self.parent_category.published:
                raise ValidationError(
                    _("Parent nodes have to be published in order to publish a child.")
                )

        if not self.published and self.get_children().filter(published=True).exists():
            raise ValidationError(
                _("Parent nodes cannot be unpublished if they have published children.")
            )
