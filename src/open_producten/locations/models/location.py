from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.core.models import BaseModel
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

    class Meta:
        abstract = True

    @property
    def address_str(self):
        return f"{self.address_line_1}, {self.address_line_2}"

    @property
    def address_line_1(self):
        return f"{self.street} {self.house_number}"

    @property
    def address_line_2(self):
        postcode = self.postcode.replace(" ", "")
        return f"{postcode} {self.city}"


class Location(BaseLocation):
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self) -> str:
        return f"{self.name}: {self.address_str}"
