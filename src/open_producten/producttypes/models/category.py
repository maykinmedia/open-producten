from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from treebeard.exceptions import InvalidMoveToDescendant
from treebeard.mp_tree import MP_MoveHandler, MP_Node

from open_producten.core.models import BaseModel


class PublishedMoveHandler(MP_MoveHandler):
    def process(self):
        if self.node.published and not self.target.published:
            raise InvalidMoveToDescendant(
                _("Published nodes cannot be moved to unpublished ones.")
            )
        return super().process()


class Category(MP_Node, BaseModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=100, help_text=_("Name of the category")
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=100,
        unique=True,
        help_text=_("Slug of the category"),
    )

    description = models.TextField(
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

    def get_build_slug(self):
        if self.is_root():
            build_slug = self.slug
        else:
            build_slug = "/".join(
                list(self.get_ancestors().values_list("slug", flat=True))
            )
            build_slug += f"/{self.slug}"
        return build_slug

    def get_absolute_url(self):
        return reverse(
            "products:category_detail", kwargs={"slug": self.get_build_slug()}
        )

    def move(self, target, pos=None):
        return PublishedMoveHandler(self, target, pos).process()
