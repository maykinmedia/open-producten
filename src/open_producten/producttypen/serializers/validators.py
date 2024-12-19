from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ...utils.serializers import get_from_serializer_data_or_instance
from ..models import PrijsOptie
from ..models.vraag import validate_onderwerp_or_product_type


class ProductTypeOrOnderwerpValidator:
    requires_context = True

    def __call__(self, value, serializer):
        onderwerp = get_from_serializer_data_or_instance("onderwerp", value, serializer)
        product_type = get_from_serializer_data_or_instance(
            "product_type", value, serializer
        )
        try:
            validate_onderwerp_or_product_type(onderwerp, product_type)
        except ValidationError as e:
            raise serializers.ValidationError({"product_type_onderwerp": e.message})


class PrijsOptieValidator:
    requires_context = True

    def __call__(self, value, serializer):
        prijs_instance = serializer.instance
        if not prijs_instance or not value.get("prijsopties"):
            return

        optie_errors = []

        current_optie_ids = set(
            prijs_instance.prijsopties.values_list("id", flat=True).distinct()
        )
        seen_optie_ids = set()

        for idx, optie in enumerate(value["prijsopties"]):
            optie_id = optie.pop("id", None)

            if not optie_id:
                continue

            if optie_id in current_optie_ids:

                if optie_id in seen_optie_ids:
                    optie_errors.append(
                        _("Dubbele optie id {} op index {}.").format(optie_id, idx)
                    )
                seen_optie_ids.add(optie_id)

            else:
                try:
                    PrijsOptie.objects.get(id=optie_id)
                    optie_errors.append(
                        _(
                            "Prijs optie id {} op index {} is niet onderdeel van het prijs object."
                        ).format(optie_id, idx)
                    )
                except PrijsOptie.DoesNotExist:
                    optie_errors.append(
                        _("Prijs optie id {} op index {} bestaat niet.").format(
                            optie_id, idx
                        )
                    )

        if optie_errors:
            raise serializers.ValidationError({"prijsopties": optie_errors})
