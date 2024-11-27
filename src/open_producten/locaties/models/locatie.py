from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from geopy.exc import GeopyError

from open_producten.utils.geocode import geocode_address
from open_producten.utils.models import BaseModel
from open_producten.utils.validators import validate_phone_number, validate_postal_code


class BaseLocatie(BaseModel):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=100,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("email adres"),
        blank=True,
    )
    telefoonnummer = models.CharField(
        verbose_name=_("telefoonnummer"),
        blank=True,
        default="",
        max_length=15,
        validators=[validate_phone_number],
    )

    straat = models.CharField(_("straat"), blank=True, max_length=250)
    huisnummer = models.CharField(
        _("huisnummer"),
        blank=True,
        max_length=250,
    )

    postcode = models.CharField(
        _("postcode"),
        max_length=7,
        validators=[validate_postal_code],
    )
    stad = models.CharField(_("stad"), max_length=250)

    coordinaten = PointField(
        _("coördinaten"),
        help_text=_("Geo coördinaten van de locatie"),
    )

    class Meta:
        abstract = True

    @property
    def address(self) -> str:
        postcode = self.postcode.replace(" ", "")
        return f"{self.straat} {self.huisnummer}, {postcode} {self.stad}"

    def clean(self):
        self.clean_geometry()

    def clean_geometry(self):
        try:
            coordinaten = geocode_address(self.address)
        except GeopyError as exc:
            raise ValidationError(
                _(
                    "Het vinden van de coördinaten van de adresgegevens is mislukt: %(exc)s"
                )
                % {"exc": exc}
            )
        except IndexError:
            raise ValidationError(_("Er zijn geen adresgegevens gegeven."))

        if not coordinaten:
            raise ValidationError(
                _(
                    "Coördinaten van het adres kunnen niet worden gevonden. "
                    "Zorg ervoor dat de adresgegevens correct zijn"
                )
            )
        self.coordinaten = coordinaten


class Locatie(BaseLocatie):
    class Meta:
        verbose_name = _("Locatie")
        verbose_name_plural = _("Locaties")

    def __str__(self) -> str:
        return f"{self.naam}: {self.address}"
