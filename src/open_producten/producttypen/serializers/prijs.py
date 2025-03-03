from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from ..models import Prijs, PrijsOptie, ProductType
from .validators import PrijsOptieValidator


class PrijsOptieSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = PrijsOptie
        fields = ("id", "bedrag", "beschrijving")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "prijs response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "prijsopties": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "bedrag": "50.99",
                        "beschrijving": "normaal",
                    }
                ],
                "actief_vanaf": "2019-08-24",
            },
            response_only=True,
        ),
        OpenApiExample(
            "prijs request",
            description="prijsOptie bedragen kunnen worden ingevuld als een getal of als string met een . of , voor de decimalen",
            value={
                "prijsopties": [
                    {"bedrag": "50.99", "beschrijving": "normaal"},
                    {"bedrag": "70.99", "beschrijving": "spoed"},
                ],
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "actief_vanaf": "2024-12-01",
            },
            request_only=True,
        ),
    ],
)
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
