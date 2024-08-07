from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.validators import validate_phone_number

from .organisation import Organisation


class Contact(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        verbose_name=_("Organisation"),
        null=True,
        blank=True,
        related_name="product_contacts",
        on_delete=models.SET_NULL,
        help_text=_("The organisation of the contact"),
    )
    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=255,
        help_text=_("First name of the contact"),
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=255,
        help_text=_("Last name of the contact"),
    )
    email = models.EmailField(
        verbose_name=_("Email address"),
        blank=True,
        help_text=_("The email address of the contact"),
    )
    phone_number = models.CharField(
        verbose_name=_("Phone number"),
        blank=True,
        max_length=15,
        validators=[validate_phone_number],
        help_text=_("The phone number of the contact"),
    )
    role = models.CharField(
        verbose_name=_("Rol"),
        blank=True,
        max_length=100,
        help_text=_("The role/function of the contact"),
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self):
        if self.organisation:
            return f"{self.organisation.name}: {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def get_mailto_link(self):
        email = self.get_email()
        if not email:
            return
        return f"mailto://{email}"

    def get_email(self):
        if self.email:
            return self.email
        return self.organisation.email

    def get_phone_number(self):
        if self.phone_number:
            return self.phone_number
        return self.organisation.phone_number
