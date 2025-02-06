from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from open_producten.locaties.models import Contact, Locatie, Organisatie
from open_producten.locaties.serializers.locatie import (
    ContactSerializer,
    LocatieSerializer,
    OrganisatieSerializer,
)

from ...utils.drf_validators import DuplicateIdValidator
from ..models import ProductType, Thema, UniformeProductNaam
from .bestand import NestedBestandSerializer
from .eigenschap import EigenschapSerializer
from .externe_code import ExterneCodeSerializer
from .link import NestedLinkSerializer
from .prijs import NestedPrijsSerializer, PrijsSerializer
from .vraag import NestedVraagSerializer


class NestedThemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thema
        fields = (
            "id",
            "naam",
            "beschrijving",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "hoofd_thema",
        )


class ProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="uri", queryset=UniformeProductNaam.objects.all()
    )

    themas = NestedThemaSerializer(many=True, read_only=True)
    thema_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Thema.objects.all(),
        source="themas",
    )

    locaties = LocatieSerializer(many=True, read_only=True)
    locatie_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Locatie.objects.all(),
        default=[],
        source="locaties",
    )

    organisaties = OrganisatieSerializer(many=True, read_only=True)
    organisatie_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Organisatie.objects.all(),
        default=[],
        source="organisaties",
    )

    contacten = ContactSerializer(many=True, read_only=True)
    contact_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Contact.objects.all(),
        default=[],
        source="contacten",
    )

    vragen = NestedVraagSerializer(many=True, read_only=True)
    prijzen = NestedPrijsSerializer(many=True, read_only=True)
    links = NestedLinkSerializer(many=True, read_only=True)
    bestanden = NestedBestandSerializer(many=True, read_only=True)

    eigenschappen = EigenschapSerializer(many=True, required=False)
    externe_codes = ExterneCodeSerializer(many=True, required=False)

    def validate_eigenschappen(self, eigenschappen: list[dict]):
        keys = set()

        for eigenschap in eigenschappen:
            if eigenschap["key"] in keys:
                raise serializers.ValidationError(
                    _(
                        "De eigenschappen van een product type moeten unieke keys hebben."
                    )
                )
            else:
                keys.add(eigenschap["key"])

        return eigenschappen

    def validate_externe_codes(self, externe_codes: list[dict]):
        systemen = set()

        for externe_code in externe_codes:
            if externe_code["systeem"] in systemen:
                raise serializers.ValidationError(
                    _(
                        "De externe codes van een product type moeten een uniek systeem hebben."
                    )
                )
            else:
                systemen.add(externe_code["systeem"])

        return externe_codes

    class Meta:
        model = ProductType
        fields = "__all__"
        validators = [
            DuplicateIdValidator(
                ["thema_ids", "locatie_ids", "organisatie_ids", "contacten_ids"]
            )
        ]

    def validate_thema_ids(self, themas: list[Thema]) -> list[Thema]:
        if len(themas) == 0:
            raise serializers.ValidationError(_("Er is minimaal één thema vereist."))
        return themas

    @transaction.atomic()
    def create(self, validated_data):
        themas = validated_data.pop("themas")
        locaties = validated_data.pop("locaties")
        organisaties = validated_data.pop("organisaties")
        contacten = validated_data.pop("contacten")
        eigenschappen = validated_data.pop("eigenschappen", [])
        externe_codes = validated_data.pop("externe_codes", [])

        product_type = ProductType.objects.create(**validated_data)
        product_type.themas.set(themas)
        product_type.locaties.set(locaties)
        product_type.organisaties.set(organisaties)
        product_type.contacten.set(contacten)

        for eigenschap in eigenschappen:
            EigenschapSerializer().create(eigenschap | {"product_type": product_type})

        for externe_code in externe_codes:
            ExterneCodeSerializer().create(
                externe_code | {"product_type": product_type}
            )

        product_type.save()
        product_type.add_contact_organisaties()
        return product_type

    @transaction.atomic()
    def update(self, instance, validated_data):
        themas = validated_data.pop("themas", None)
        locaties = validated_data.pop("locaties", None)
        organisaties = validated_data.pop("organisaties", None)
        contacten = validated_data.pop("contacten", None)
        eigenschappen = validated_data.pop("eigenschappen", None)
        externe_codes = validated_data.pop("externe_codes", None)

        instance = super().update(instance, validated_data)

        if themas:
            instance.themas.set(themas)
        if locaties:
            instance.locaties.set(locaties)
        if organisaties:
            instance.organisaties.set(organisaties)
        if contacten:
            instance.contacten.set(contacten)

        if eigenschappen is not None:
            current_eigenschappen = set(
                instance.eigenschappen.values_list("key", flat=True)
            )
            seen_eigenschappen = set()
            for eigenschap in eigenschappen:
                key = eigenschap.pop("key")
                if key in current_eigenschappen:
                    existing_eigenschap = instance.eigenschappen.get(key=key)
                    EigenschapSerializer().update(existing_eigenschap, eigenschap)
                    seen_eigenschappen.add(key)
                else:
                    EigenschapSerializer().create(
                        eigenschap | {"product_type": instance, "key": key}
                    )
            instance.eigenschappen.filter(
                key__in=(current_eigenschappen - seen_eigenschappen)
            ).delete()

        if externe_codes is not None:
            current_externe_codes = set(
                instance.externe_codes.values_list("systeem", flat=True)
            )
            seen_externe_codes = set()
            for externe_code in externe_codes:
                systeem = externe_code.pop("systeem")
                if systeem in current_externe_codes:
                    existing_externe_code = instance.externe_codes.get(systeem=systeem)
                    ExterneCodeSerializer().update(existing_externe_code, externe_code)
                    seen_externe_codes.add(systeem)
                else:
                    ExterneCodeSerializer().create(
                        externe_code | {"product_type": instance, "systeem": systeem}
                    )
            instance.externe_codes.filter(
                systeem__in=(current_externe_codes - seen_externe_codes)
            ).delete()

        instance.save()
        instance.add_contact_organisaties()
        return instance


class ProductTypeActuelePrijsSerializer(serializers.ModelSerializer):
    upl_uri = serializers.ReadOnlyField(source="uniforme_product_naam.uri")
    upl_naam = serializers.ReadOnlyField(source="uniforme_product_naam.naam")
    actuele_prijs = PrijsSerializer(allow_null=True)

    class Meta:
        model = ProductType
        fields = ("id", "naam", "upl_naam", "upl_uri", "actuele_prijs")
