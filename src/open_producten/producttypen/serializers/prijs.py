from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import Prijs, PrijsOptie, ProductType
from .validators import PrijsOptieValidator


class PrijsOptieSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    bedrag = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        localize=True,
        help_text=_("Het bedrag van de prijs optie."),
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = PrijsOptie
        fields = ("id", "bedrag", "beschrijving")


class PrijsSerializer(serializers.ModelSerializer):
    prijsopties = PrijsOptieSerializer(many=True)
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Prijs
        fields = ("id", "product_type_id", "prijsopties", "actief_vanaf")
        validators = [PrijsOptieValidator()]

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

        if opties is not None:
            current_optie_ids = set(
                prijs.prijsopties.values_list("id", flat=True).distinct()
            )
            seen_optie_ids = set()

            for optie in opties:
                optie_id = optie.pop("id", None)
                if optie_id is None:
                    PrijsOptie.objects.create(prijs=prijs, **optie)

                else:
                    existing_optie = PrijsOptie.objects.get(id=optie_id)
                    existing_optie.bedrag = optie["bedrag"]
                    existing_optie.beschrijving = optie["beschrijving"]
                    existing_optie.save()

            PrijsOptie.objects.filter(
                id__in=(current_optie_ids - seen_optie_ids)
            ).delete()

        return prijs


class NestedPrijsSerializer(PrijsSerializer):
    class Meta:
        model = Prijs
        fields = ("id", "prijsopties", "actief_vanaf")
