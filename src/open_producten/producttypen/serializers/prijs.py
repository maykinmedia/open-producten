from django.db import transaction

from rest_framework import serializers

from ...utils.drf_validators import NestedObjectsValidator
from ..models import Prijs, PrijsOptie, ProductType
from ..models.prijs import PrijsRegel
from .validators import PrijsOptieRegelValidator


class PrijsOptieSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = PrijsOptie
        fields = ("id", "bedrag", "beschrijving")


class PrijsRegelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = PrijsRegel
        fields = ("id", "dmn_url", "beschrijving")


class PrijsSerializer(serializers.ModelSerializer):
    prijsopties = PrijsOptieSerializer(many=True, required=False)
    prijsregels = PrijsRegelSerializer(many=True, required=False)
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Prijs
        fields = ("id", "product_type_id", "prijsopties", "prijsregels", "actief_vanaf")
        validators = [
            PrijsOptieRegelValidator(),
            NestedObjectsValidator("prijsopties", PrijsOptie),
            NestedObjectsValidator("prijsregels", PrijsRegel),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        prijsopties = validated_data.pop("prijsopties", [])
        prijsregels = validated_data.pop("prijsregels", [])
        product_type = validated_data.pop("product_type")

        prijs = Prijs.objects.create(**validated_data, product_type=product_type)

        for optie in prijsopties:
            PrijsOptieSerializer().create(optie | {"prijs": prijs})

        for regel in prijsregels:
            PrijsRegelSerializer().create(regel | {"prijs": prijs})

        return prijs

    @transaction.atomic()
    def update(self, instance, validated_data):
        opties = validated_data.pop("prijsopties", None)
        regels = validated_data.pop("prijsregels", None)
        prijs = super().update(instance, validated_data)

        if opties is not None:
            current_optie_ids = set(prijs.prijsopties.values_list("id", flat=True))
            seen_optie_ids = set()

            for optie in opties:
                optie_id = optie.pop("id", None)
                if optie_id is None:
                    PrijsOptieSerializer().create(optie | {"prijs": prijs})

                else:
                    existing_optie = PrijsOptie.objects.get(id=optie_id)
                    PrijsOptieSerializer().update(existing_optie, optie)
                    seen_optie_ids.add(optie_id)

            prijs.prijsopties.filter(
                id__in=(current_optie_ids - seen_optie_ids)
            ).delete()

        if regels is not None:
            current_regel_ids = set(
                prijs.prijsregels.values_list("id", flat=True).distinct()
            )
            seen_regel_ids = set()

            for regel in regels:
                regel_id = regel.pop("id", None)
                if regel_id is None:
                    PrijsRegelSerializer().create(regel | {"prijs": prijs})

                else:
                    existing_regel = PrijsRegel.objects.get(id=regel_id)
                    PrijsRegelSerializer().update(existing_regel, regel)
                    seen_regel_ids.add(regel_id)

            prijs.prijsregels.filter(
                id__in=(current_regel_ids - seen_regel_ids)
            ).delete()

        return prijs


class NestedPrijsSerializer(PrijsSerializer):
    class Meta:
        model = Prijs
        fields = ("id", "prijsopties", "actief_vanaf")
