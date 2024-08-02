from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BasePublishableModel

from .category import Category
from .condition import Condition
from .tag import Tag
from .upn import UniformProductName


class CategoryProductType(models.Model):
    """
    Through-model for Category-ProductType m2m-relations.
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_type = models.ForeignKey("ProductType", on_delete=models.CASCADE)


class ProductType(BasePublishableModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=100, help_text=_("Name of the product type")
    )

    summary = models.TextField(
        verbose_name=_("Summary"),
        default="",
        max_length=300,
        help_text=_(
            "Short description of the product type, limited to 300 characters."
        ),
    )

    icon = models.ImageField(
        verbose_name=_("Icon"),
        null=True,
        blank=True,
        help_text=_("Icon of the product type"),
    )

    image = models.ImageField(
        verbose_name=_("Image"),
        null=True,
        blank=True,
        help_text=_("Main image of the product type"),
    )

    form_link = models.URLField(
        verbose_name=_("Form link"),
        blank=True,
        default="",
        help_text=_("Action link to request the product type."),
    )

    content = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Product type content with build-in WYSIWYG editor."),
    )

    related_product_types = models.ManyToManyField(
        "ProductType",
        verbose_name=_("Related product types"),
        blank=True,
        help_text=_("Related product types to this product type"),
    )

    keywords = ArrayField(
        models.CharField(max_length=100, blank=True),
        verbose_name=_("Keywords"),
        default=list,
        blank=True,
        help_text=_("List of keywords for search"),
    )

    uniform_product_name = models.ForeignKey(
        UniformProductName,
        verbose_name=_("Uniform Product name"),
        on_delete=models.CASCADE,
        help_text=_("Uniform product name defined by Dutch gov"),
        related_name="product_types",
    )

    conditions = models.ManyToManyField(
        Condition,
        related_name="product_types",
        verbose_name=_("Conditions"),
        blank=True,
        help_text=_("Conditions applicable for the product type"),
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name=_("Tags"),
        blank=True,
        related_name="product_types",
        help_text=_("Tags which the product type is linked to"),
    )

    categories = models.ManyToManyField(
        Category,
        verbose_name=_("Categories"),
        blank=True,
        related_name="product_types",
        help_text=_("Categories which the product type is linked to"),
        through=CategoryProductType,
    )

    class Meta:
        verbose_name = _("Product type")
        verbose_name_plural = _("Product types")

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        now = date.today()
        return self.prices.filter(valid_from__lte=now).order_by("valid_from").last()
