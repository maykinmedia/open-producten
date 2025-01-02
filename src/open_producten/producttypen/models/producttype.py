from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from markdownx.models import MarkdownxField

# from open_producten.locations.models import Contact, Location, Organisation
from open_producten.utils.models import BasePublishableModel

from .thema import Thema
from .upn import UniformeProductNaam


class ProductType(BasePublishableModel):
    naam = models.CharField(
        verbose_name=_("product type naam"),
        max_length=100,
        help_text=_("naam van het product type."),
    )

    samenvatting = models.TextField(
        verbose_name=_("samenvatting"),
        default="",
        max_length=300,
        help_text=_("Korte beschrijving van het product type, maximaal 300 karakters."),
    )

    beschrijving = MarkdownxField(
        verbose_name=_("beschrijving"),
        help_text=_("Product type beschrijving, ondersteund markdown format."),
    )

    keywords = ArrayField(
        models.CharField(max_length=100, blank=True),
        verbose_name=_("Keywords"),
        default=list,
        blank=True,
        help_text=_("Lijst van keywords waarop kan worden gezocht."),
    )

    uniforme_product_naam = models.ForeignKey(
        UniformeProductNaam,
        verbose_name=_("Uniforme Product naam"),
        on_delete=models.CASCADE,
        help_text=_("Uniforme product naam gedefinieerd door de overheid."),
        related_name="product_typen",
    )

    themas = models.ManyToManyField(
        Thema,
        verbose_name=_("thema's"),
        blank=True,
        related_name="product_typen",
        help_text=_("thema's waaraan het product type is gelinkt."),
    )

    # organisations = models.ManyToManyField(
    #     Organisation,
    #     verbose_name=_("Organisations"),
    #     blank=True,
    #     related_name="products",
    #     help_text=_("Organisations which provides this product"),
    # )
    #
    # contacts = models.ManyToManyField(
    #     Contact,
    #     verbose_name=_("Contacts"),
    #     related_name="products",
    #     blank=True,
    #     help_text=_("The contacts responsible for the product"),
    # )
    #
    # locations = models.ManyToManyField(
    #     Location,
    #     verbose_name=_("Locations"),
    #     related_name="products",
    #     blank=True,
    #     help_text=_("Locations where the product is available at."),
    # )

    class Meta:
        verbose_name = _("Product type")
        verbose_name_plural = _("Product typen")

    def __str__(self):
        return self.naam

    # def clean(self):
    #     for contact in self.contacts.all():
    #         if (
    #             contact.organisation_id is not None
    #             and not self.organisations.filter(id=contact.organisation_id).exists()
    #         ):
    #             self.organisations.add(contact.organisation)

    @property
    def actuele_prijs(self):
        now = date.today()
        return (
            self.prijzen.filter(actief_vanaf__lte=now).order_by("actief_vanaf").last()
        )
