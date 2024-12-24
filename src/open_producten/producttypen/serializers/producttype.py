from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ...utils.drf_validators import DuplicateIdValidator
from ..models import Onderwerp, ProductType, UniformeProductNaam
from .bestand import NestedBestandSerializer
from .link import NestedLinkSerializer
from .prijs import NestedPrijsSerializer, PrijsSerializer
from .vraag import NestedVraagSerializer

# from open_producten.locaties.models import Contact, Locatie, Organisatie
# from open_producten.locaties.serializers.location import (
#     ContactSerializer,
#     LocationSerializer,
#     OrganisationSerializer,
# )


class NestedOnderwerpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Onderwerp
        fields = (
            "id",
            "naam",
            "beschrijving",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "hoofd_onderwerp",
        )


class ProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="uri", queryset=UniformeProductNaam.objects.all()
    )

    onderwerpen = NestedOnderwerpSerializer(many=True, read_only=True)
    onderwerp_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Onderwerp.objects.all(),
        source="onderwerpen",
    )

    # locaties = LocationSerializer(many=True, read_only=True)
    # locatie_ids = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     write_only=True,
    #     queryset=Locatie.objects.all(),
    #     default=[],
    #     source="locaties",
    # )
    #
    # organisaties = OrganisationSerializer(many=True, read_only=True)
    # organisatie_ids = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     write_only=True,
    #     queryset=Organisatie.objects.all(),
    #     default=[],
    #     source="organisaties",
    # )
    #
    # contacts = ContactSerializer(many=True, read_only=True)
    # contact_ids = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     write_only=True,
    #     queryset=Contact.objects.all(),
    #     default=[],
    #     source="contacten",
    # )

    vragen = NestedVraagSerializer(many=True, read_only=True)
    prijzen = NestedPrijsSerializer(many=True, read_only=True)
    links = NestedLinkSerializer(many=True, read_only=True)
    bestanden = NestedBestandSerializer(many=True, read_only=True)

    class Meta:
        model = ProductType
        fields = "__all__"
        validators = [DuplicateIdValidator(["onderwerp_ids"])]

    def validate_onderwerp_ids(self, onderwerpen: list[Onderwerp]) -> list[Onderwerp]:
        if len(onderwerpen) == 0:
            raise serializers.ValidationError(
                _("Er is minimaal één onderwerp vereist.")
            )
        return onderwerpen

    @transaction.atomic()
    def create(self, validated_data):
        onderwerpen = validated_data.pop("onderwerpen")
        # locaties = validated_data.pop("locaties")
        # organisaties = validated_data.pop("organisaties")
        # contacten = validated_data.pop("contacten")

        product_type = ProductType.objects.create(**validated_data)
        product_type.onderwerpen.set(onderwerpen)

        product_type.save()

        return product_type

    @transaction.atomic()
    def update(self, instance, validated_data):
        onderwerpen = validated_data.pop("onderwerpen", None)
        # locaties = validated_data.pop("locaties", None)
        # organisaties = validated_data.pop("organisaties", None)
        # contacten = validated_data.pop("contacten", None)
        instance = super().update(instance, validated_data)
        if onderwerpen:
            instance.onderwerpen.set(onderwerpen)
        instance.save()

        return instance


class ProductTypeActuelePrijsSerializer(serializers.ModelSerializer):
    upl_uri = serializers.ReadOnlyField(source="uniforme_product_naam.uri")
    upl_naam = serializers.ReadOnlyField(source="uniforme_product_naam.naam")
    actuele_prijs = PrijsSerializer(allow_null=True)

    class Meta:
        model = ProductType
        fields = ("id", "naam", "upl_naam", "upl_uri", "actuele_prijs")
