from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ...utils.serializers import get_from_serializer_data_or_instance
from ..models import PrijsOptie
from ..models.thema import disallow_self_reference, validate_gepubliceerd_state
from ..models.vraag import validate_thema_or_product_type


class ProductTypeOrThemaValidator:
    requires_context = True

    def __call__(self, value, serializer):
        thema = get_from_serializer_data_or_instance("thema", value, serializer)
        product_type = get_from_serializer_data_or_instance(
            "product_type", value, serializer
        )
        try:
            validate_thema_or_product_type(thema, product_type)
        except ValidationError as e:
            raise serializers.ValidationError({"product_type_or_thema": e.message})


class ThemaGepubliceerdStateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        hoofd_thema = get_from_serializer_data_or_instance(
            "hoofd_thema", value, serializer
        )
        gepubliceerd = get_from_serializer_data_or_instance(
            "gepubliceerd", value, serializer
        )
        sub_themas = serializer.instance.sub_themas if serializer.instance else None

        try:
            validate_gepubliceerd_state(hoofd_thema, gepubliceerd, sub_themas)
        except ValidationError as e:
            raise serializers.ValidationError({"hoofd_thema": e.message})


class ThemaSelfReferenceValidator:
    requires_context = True

    def __call__(self, value, serializer):
        thema = serializer.instance
        hoofd_thema = get_from_serializer_data_or_instance(
            "hoofd_thema", value, serializer
        )

        try:
            disallow_self_reference(thema, hoofd_thema)
        except ValidationError as e:
            raise serializers.ValidationError({"hoofd_thema": e.message})


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
                        _("Dubbel id: {} op index {}.").format(optie_id, idx)
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
