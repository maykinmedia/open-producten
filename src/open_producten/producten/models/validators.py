import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_bsn(bsn: str):
    """
    Validates that a bsn number is 9 digits and runs the 11 check.
    """

    if not re.match(r"^[0-9]{9}$", bsn):
        raise ValidationError(_("Een bsn nummer bestaat uit 9 cijfers."))

    total = sum(int(num) * (9 - i) for i, num in enumerate(bsn[:8]))
    total += int(bsn[8]) * -1

    if total == 0 or total % 11 != 0:
        raise ValidationError(_("Ongeldig bsn number."))
