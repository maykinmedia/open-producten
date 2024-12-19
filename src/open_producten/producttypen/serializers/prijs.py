from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import Prijs, PrijsOptie, ProductType


class PrijsOptieSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = PrijsOptie
        fields = ("id", "bedrag", "beschrijving")


class PrijsSerializer(serializers.ModelSerializer):
    prijsopties = PrijsOptieSerializer(many=True, default=[])
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Prijs
        fields = ("id", "product_type_id", "prijsopties", "actief_vanaf")

    def validate_prijsopties(self, opties: list[PrijsOptie]) -> list[PrijsOptie]:
        if len(opties) == 0:
            raise serializers.ValidationError(_("Er is minimaal één optie vereist."))
        return opties

    @transaction.atomic()
    def create(self, validated_data):
        prijsopties = validated_data.pop("prijsopties")
        product_type = validated_data.pop("product_type")

        prijs = Prijs.objects.create(**validated_data, product_type=product_type)

        for optie in prijsopties:
            PrijsOptie.objects.create(prijs=prijs, **optie)

        return prijs

    @transaction.atomic()
    def update(self, instance, validated_data):
        opties = validated_data.pop("prijsopties", None)
        prijs = super().update(instance, validated_data)
        optie_errors = []

        if opties is not None:
            current_optie_ids = set(
                prijs.prijsopties.values_list("id", flat=True).distinct()
            )
            seen_optie_ids = set()
            for idx, optie in enumerate(opties):
                optie_id = optie.pop("id", None)
                if optie_id is None:
                    PrijsOptie.objects.create(prijs=prijs, **optie)

                elif optie_id in current_optie_ids:

                    if optie_id in seen_optie_ids:
                        optie_errors.append(
                            _("Dubbele optie id {} op index {}.").format(optie_id, idx)
                        )
                    seen_optie_ids.add(optie_id)

                    existing_optie = PrijsOptie.objects.get(id=optie_id)
                    existing_optie.bedrag = optie["bedrag"]
                    existing_optie.beschrijving = optie["beschrijving"]
                    existing_optie.save()

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

            PrijsOptie.objects.filter(
                id__in=(current_optie_ids - seen_optie_ids)
            ).delete()

        return prijs
