from django.db import transaction
from django.utils.translation import gettext_lazy as _

from django_json_schema.models import JsonSchema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from open_producten.locaties.models import Contact, Locatie, Organisatie
from open_producten.locaties.serializers.locatie import (
    ContactSerializer,
    LocatieSerializer,
    OrganisatieSerializer,
)

from ...utils.drf_validators import DuplicateIdValidator
from ..models import ProductType, Thema, UniformeProductNaam
from . import JsonSchemaSerializer
from .bestand import NestedBestandSerializer
from .externe_code import ExterneCodeSerializer, NestedExterneCodeSerializer
from .link import NestedLinkSerializer
from .parameter import NestedParameterSerializer, ParameterSerializer
from .prijs import NestedPrijsSerializer, PrijsSerializer


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


class ProductTypeSerializer(TranslatableModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="naam", queryset=UniformeProductNaam.objects.all()
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

    prijzen = NestedPrijsSerializer(many=True, read_only=True)
    links = NestedLinkSerializer(many=True, read_only=True)
    bestanden = NestedBestandSerializer(many=True, read_only=True)

    verbruiksobject_schema = JsonSchemaSerializer(read_only=True)
    verbruiksobject_schema_id = serializers.PrimaryKeyRelatedField(
        source="verbruiksobject_schema",
        queryset=JsonSchema.objects.all(),
        write_only=True,
        help_text=_(
            "JSON schema om het verbruiksobject van een gerelateerd product te valideren."
        ),
        required=False,
    )

    naam = serializers.CharField(
        required=True, max_length=255, help_text=_("naam van het product type.")
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=_("Korte beschrijving van het product type."),
    )

    taal = serializers.SerializerMethodField(
        read_only=True, help_text=_("De huidige taal van het product type.")
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_taal(self, obj):
        requested_language = self.context["request"].LANGUAGE_CODE
        return requested_language if obj.has_translation(requested_language) else "nl"

    externe_codes = NestedExterneCodeSerializer(many=True, required=False)
    parameters = NestedParameterSerializer(many=True, required=False)

    def _validate_key_value_model_keys(
        self, data_list: list[dict], unique_field: str, error_message: str
    ):
        seen = set()

        for data in data_list:
            if data[unique_field] in seen:
                raise serializers.ValidationError(
                    error_message.format(data[unique_field]), code="unique"
                )
            seen.add(data[unique_field])

        return data_list

    def validate_externe_codes(self, externe_codes: list[dict]):
        return self._validate_key_value_model_keys(
            externe_codes,
            "naam",
            _("Er bestaat al een externe code met de naam {} voor dit ProductType."),
        )

    def validate_parameters(self, parameters: list[dict]):
        return self._validate_key_value_model_keys(
            parameters,
            "naam",
            _("Er bestaat al een parameter met de naam {} voor dit ProductType."),
        )

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
        naam = validated_data.pop("naam")
        samenvatting = validated_data.pop("samenvatting")
        externe_codes = validated_data.pop("externe_codes", [])
        parameters = validated_data.pop("parameters", [])

        product_type = ProductType.objects.create(**validated_data)
        product_type.themas.set(themas)
        product_type.locaties.set(locaties)
        product_type.organisaties.set(organisaties)
        product_type.contacten.set(contacten)

        self.set_externe_codes(
            [
                externe_code | {"product_type": product_type.id}
                for externe_code in externe_codes
            ]
        )

        self.set_parameters(
            [parameter | {"product_type": product_type.id} for parameter in parameters]
        )

        product_type.set_current_language("nl")
        product_type.naam = naam
        product_type.samenvatting = samenvatting

        product_type.add_contact_organisaties()
        return product_type

    @transaction.atomic()
    def update(self, instance, validated_data):
        themas = validated_data.pop("themas", None)
        locaties = validated_data.pop("locaties", None)
        organisaties = validated_data.pop("organisaties", None)
        contacten = validated_data.pop("contacten", None)

        naam = validated_data.pop("naam", None)
        samenvatting = validated_data.pop("samenvatting", None)
        externe_codes = validated_data.pop("externe_codes", None)
        parameters = validated_data.pop("parameters", None)

        instance = super().update(instance, validated_data)

        if themas:
            instance.themas.set(themas)
        if locaties:
            instance.locaties.set(locaties)
        if organisaties:
            instance.organisaties.set(organisaties)
        if contacten:
            instance.contacten.set(contacten)

        if externe_codes is not None:
            instance.externe_codes.all().delete()
            self.set_externe_codes(
                [
                    externe_code | {"product_type": instance.id}
                    for externe_code in externe_codes
                ]
            )

        if parameters is not None:
            instance.parameters.all().delete()
            self.set_parameters(
                [parameter | {"product_type": instance.id} for parameter in parameters]
            )

        instance.set_current_language("nl")
        if naam:
            instance.naam = naam
        if samenvatting:
            instance.samenvatting = samenvatting

        instance.add_contact_organisaties()
        return instance

    def set_externe_codes(self, externe_codes: list[dict]):
        externe_code_serializer = ExterneCodeSerializer(
            data=externe_codes,
            many=True,
        )
        externe_code_serializer.is_valid(raise_exception=True)
        externe_code_serializer.save()

    def set_parameters(self, parameters: list[dict]):
        parameter_serializer = ParameterSerializer(
            data=parameters,
            many=True,
        )
        parameter_serializer.is_valid(raise_exception=True)
        parameter_serializer.save()


class ProductTypeActuelePrijsSerializer(serializers.ModelSerializer):
    upl_uri = serializers.ReadOnlyField(source="uniforme_product_naam.uri")
    upl_naam = serializers.ReadOnlyField(source="uniforme_product_naam.naam")
    actuele_prijs = PrijsSerializer(allow_null=True)

    class Meta:
        model = ProductType
        fields = ("id", "code", "upl_naam", "upl_uri", "actuele_prijs")


class ProductTypeTranslationSerializer(serializers.ModelSerializer):

    naam = serializers.CharField(
        required=True, max_length=255, help_text=_("naam van het producttype.")
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=_("Korte beschrijving van het producttype."),
    )

    class Meta:
        model = ProductType
        fields = (
            "id",
            "naam",
            "samenvatting",
        )
