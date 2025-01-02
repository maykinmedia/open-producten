from django.utils.translation import gettext_lazy as _

from .locatie import BaseLocatie


class Organisatie(BaseLocatie):
    class Meta:
        verbose_name = _("Organisatie")
        verbose_name_plural = _("Organisaties")

    def __str__(self):
        return f"{self.naam}"
