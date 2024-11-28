from django.db import transaction
from django.utils.translation import gettext as _

from rest_framework import serializers

# from open_producten.locaties.models import Contact, Locatie, Organisatie
# from open_producten.locaties.serializers.location import (
#     ContactSerializer,
#     LocationSerializer,
#     OrganisationSerializer,
# )
from open_producten.utils.serializers import build_array_duplicates_error_message

from ..models import Onderwerp, ProductType, UniformeProductNaam
from .children import (
    BestandSerializer,
    LinkSerializer,
    PrijsSerializer,
    VraagSerializer,
)


class SimpleOnderwerpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Onderwerp
        exclude = ("path", "depth", "numchild")


class ProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="uri", queryset=UniformeProductNaam.objects.all()
    )

    onderwerpen = SimpleOnderwerpSerializer(many=True, read_only=True)
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

    vragen = VraagSerializer(many=True, read_only=True)
    prijzen = PrijsSerializer(many=True, read_only=True)
    links = LinkSerializer(many=True, read_only=True)
    bestanden = BestandSerializer(many=True, read_only=True)

    class Meta:
        model = ProductType
        fields = "__all__"

    def validate_onderwerp_ids(self, onderwerpen: list[Onderwerp]) -> list[Onderwerp]:
        if len(onderwerpen) == 0:
            raise serializers.ValidationError(
                _("Er is minimaal één onderwerp vereist.")
            )
        return onderwerpen

    def _handle_relations(
        self,
        *,
        instance,
        onderwerpen: list[Onderwerp],
        # locaties: list[Locatie],
        # organisaties: list[Organisatie],
        # contacten: list[Contact],
    ) -> None:
        errors = dict()
        if onderwerpen is not None:
            build_array_duplicates_error_message(onderwerpen, "onderwerp_ids", errors)
            instance.onderwerpen.set(onderwerpen)
        # if locaties is not None:
        #     build_array_duplicates_error_message(locaties, "locatie_ids", errors)
        #     instance.locations.set(locaties)
        # if organisaties is not None:
        #     build_array_duplicates_error_message(
        #         organisaties, "organisatie_ids", errors
        #     )
        #     instance.organisations.set(organisaties)
        # if contacten is not None:
        #     build_array_duplicates_error_message(contacten, "contact_ids", errors)
        #     instance.contacten.set(contacten)

        if errors:
            raise serializers.ValidationError(errors)

    @transaction.atomic()
    def create(self, validated_data):
        onderwerpen = validated_data.pop("onderwerpen")
        # locaties = validated_data.pop("locaties")
        # organisaties = validated_data.pop("organisaties")
        # contacten = validated_data.pop("contacten")

        product_type = ProductType.objects.create(**validated_data)

        self._handle_relations(
            instance=product_type,
            onderwerpen=onderwerpen,
            # locaties=locaties,
            # organisaties=organisaties,
            # contacten=contacten,
        )
        product_type.clean()
        product_type.save()

        return product_type

    @transaction.atomic()
    def update(self, instance, validated_data):
        onderwerpen = validated_data.pop("onderwerpen", None)
        # locaties = validated_data.pop("locaties", None)
        # organisaties = validated_data.pop("organisaties", None)
        # contacten = validated_data.pop("contacten", None)

        instance = super().update(instance, validated_data)
        self._handle_relations(
            instance=instance,
            onderwerpen=onderwerpen,
            # locaties=locaties,
            # organisaties=organisaties,
            # contacten=contacten,
        )
        instance.clean()
        instance.save()

        return instance


class ProductTypeActuelePrijsSerializer(serializers.ModelSerializer):
    upl_uri = serializers.ReadOnlyField(source="uniforme_product_naam.uri")
    upl_naam = serializers.ReadOnlyField(source="uniforme_product_naam.naam")
    actuele_prijs = PrijsSerializer(allow_null=True)

    class Meta:
        model = ProductType
        fields = ("id", "naam", "upl_naam", "upl_uri", "actuele_prijs")
