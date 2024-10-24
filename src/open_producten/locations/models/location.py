from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from geopy.exc import GeopyError

from open_producten.utils.geocode import geocode_address
from open_producten.utils.models import BaseModel
from open_producten.utils.validators import validate_phone_number, validate_postal_code


class BaseLocation(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("Email address"),
        blank=True,
    )
    phone_number = models.CharField(
        verbose_name=_("Phone number"),
        blank=True,
        default="",
        max_length=15,
        validators=[validate_phone_number],
    )

    street = models.CharField(
        _("street"), blank=True, max_length=250, help_text=_("Address street")
    )
    house_number = models.CharField(
        _("house number"),
        blank=True,
        max_length=250,
    )

    postcode = models.CharField(
        _("postcode"),
        max_length=7,
        help_text=_("Address postcode"),
        validators=[validate_postal_code],
    )
    city = models.CharField(_("city"), max_length=250, help_text=_("Address city"))

    coordinates = PointField(
        _("coordinates"),
        help_text=_("Geo coordinates of the location"),
    )

    class Meta:
        abstract = True

    @property
    def address(self) -> str:
        postcode = self.postcode.replace(" ", "")
        return f"{self.street} {self.house_number}, {postcode} {self.city}"

    def clean(self):
        self.clean_geometry()

    def clean_geometry(self):
        try:
            coordinates = geocode_address(self.address)
        except GeopyError as exc:
            raise ValidationError(
                _("Locating geo coordinates has failed: %(exc)s") % {"exc": exc}
            )
        except IndexError:
            raise ValidationError(_("No location data was provided"))

        if not coordinates:
            raise ValidationError(
                _(
                    "Geo coordinates of the address can't be found. "
                    "Make sure that the address data are correct"
                )
            )
        self.coordinates = coordinates


class Location(BaseLocation):
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self) -> str:
        return f"{self.name}: {self.address}"
