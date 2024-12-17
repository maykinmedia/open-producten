from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from markdownx.models import MarkdownxField

from open_producten.locaties.models import Contact, Locatie, Organisatie
from open_producten.utils.fields import ChoiceArrayField
from open_producten.utils.models import BasePublishableModel

from .onderwerp import Onderwerp
from .upn import UniformeProductNaam


class OnderwerpProductType(models.Model):
    """
    Through-model for Onderwerp-ProductType m2m-relations.
    """

    onderwerp = models.ForeignKey(Onderwerp, on_delete=models.CASCADE)
    product_type = models.ForeignKey("ProductType", on_delete=models.CASCADE)


class ProductStateChoices(models.TextChoices):
    GEREERD = "gereed", _("Gereed")
    ACTIEF = "actief", _("Actief")
    INGETROKKEN = "ingetrokken", _("Ingetrokken")
    GEWEIGERD = "geweigerd", _("Geweigerd")
    VERLOPEN = "verlopen", _("Verlopen")


class ProductType(BasePublishableModel):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=100,
        help_text=_("naam van het product type."),
    )

    code = models.CharField(
        verbose_name=_("code"),
        max_length=100,
        help_text=_("code van het product type."),
        unique=True,
    )

    toegestane_statussen = ChoiceArrayField(
        models.CharField(choices=ProductStateChoices.choices),
        verbose_name=_("toegestane statussen"),
        default=list,
        blank=True,
        help_text=_("toegestane statussen voor producten van dit type."),
    )

    samenvatting = models.TextField(
        verbose_name=_("samenvatting"),
        default="",
        max_length=300,
        help_text=_("Korte beschrijving van het product type, maximaal 300 karakters."),
    )

    beschrijving = MarkdownxField(
        verbose_name=_("beschrijving"),
        help_text=_("Product type beschrijving met WYSIWYG editor."),
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

    onderwerpen = models.ManyToManyField(
        Onderwerp,
        verbose_name=_("onderwerp"),
        blank=True,
        related_name="product_typen",
        help_text=_("onderwerpen waaraan het product type is gelinkt."),
        through=OnderwerpProductType,
    )

    organisaties = models.ManyToManyField(
        Organisatie,
        verbose_name=_("organisaties"),
        blank=True,
        related_name="product_typen",
        help_text=_("organisaties die dit het product aanbieden."),
    )

    contacten = models.ManyToManyField(
        Contact,
        verbose_name=_("contacten"),
        related_name="product_typen",
        blank=True,
        help_text=_("De contacten verantwoordelijk voor het product type."),
    )

    locaties = models.ManyToManyField(
        Locatie,
        verbose_name=_("locaties"),
        related_name="product_typen",
        blank=True,
        help_text=_("De locaties waar het product beschikbaar is."),
    )

    class Meta:
        verbose_name = _("Product type")
        verbose_name_plural = _("Product typen")

    def __str__(self):
        return self.naam

    def clean(self):
        for contact in self.contacten.all():
            if (
                contact.organisatie_id is not None
                and not self.organisaties.filter(id=contact.organisatie_id).exists()
            ):
                self.organisaties.add(contact.organisatie)

        for product in self.producten.all():
            if (
                product.status is not None
                and product.status not in self.toegestane_statussen
            ):
                raise ValidationError(
                    {
                        "toegestane_statussen": _(
                            "Een product van {} heeft de status '{}'.".format(
                                self.naam, ProductStateChoices(product.status).label
                            )
                        )
                    }
                )

    @property
    def actuele_prijs(self):
        now = date.today()
        return (
            self.prijzen.filter(actief_vanaf__lte=now).order_by("actief_vanaf").last()
        )
