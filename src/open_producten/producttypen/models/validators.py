from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .externeverwijzingconfig import ExterneVerwijzingConfig


def validate_prijs_optie_xor_regel(optie_count: int, regel_count: int):

    if optie_count and regel_count:
        raise ValidationError(_("Een prijs kan niet zowel opties als regels hebben."))

    if optie_count == 0 and regel_count == 0:
        raise ValidationError(
            _("Een prijs moet één of meerdere opties of regels hebben.")
        )


def validate_thema_gepubliceerd_state(hoofd_thema, gepubliceerd, sub_themas=None):
    if gepubliceerd and hoofd_thema and not hoofd_thema.gepubliceerd:
        raise ValidationError(
            _(
                "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
            )
        )

    if (
        not gepubliceerd
        and sub_themas
        and sub_themas.filter(gepubliceerd=True).exists()
    ):
        raise ValidationError(
            _(
                "Thema's kunnen niet ongepubliceerd worden als ze gepubliceerde sub-thema's hebben."
            )
        )


def disallow_hoofd_thema_self_reference(thema, hoofd_thema):
    if thema and hoofd_thema and thema.id == hoofd_thema.id:
        raise ValidationError("Een thema kan niet zijn eigen hoofd thema zijn.")


def check_processen_url():
    if not ExterneVerwijzingConfig.get_solo().processen_url:
        raise ValidationError(
            _("De processen url is niet geconfigureerd in de externe verwijzing config")
        )


def check_verzoektypen_url():
    if not ExterneVerwijzingConfig.get_solo().verzoektypen_url:
        raise ValidationError(
            _(
                "De verzoektypen url is niet geconfigureerd in de externe verwijzing config"
            )
        )


def check_zaaktypen_url():
    if not ExterneVerwijzingConfig.get_solo().processen_url:
        raise ValidationError(
            _("De zaaktypen url is niet geconfigureerd in de externe verwijzing config")
        )
