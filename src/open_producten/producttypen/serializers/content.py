from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from open_producten.producttypen.models import ContentElement, ContentLabel, ProductType


class ContentElementSerializer(TranslatableModelSerializer):
    labels = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=ContentLabel.objects.all(),
        many=True,
        required=False,
    )

    content = serializers.CharField(
        required=True,
        max_length=100,
        help_text=_("De content van dit content element."),
    )

    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    taal = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_taal(self, obj):
        requested_language = self.context["view"].get_requested_language()
        return requested_language if obj.has_translation(requested_language) else "nl"

    class Meta:
        model = ContentElement
        fields = ("id", "content", "labels", "product_type_id", "taal")

    def create(self, validated_data):
        content = validated_data.pop("content")

        content_element = super().create(validated_data)
        content_element.set_current_language("nl")
        content_element.content = content

        return content_element

    def update(self, instance, validated_data):
        content = validated_data.pop("content", None)

        instance = super().update(instance, validated_data)

        instance.set_current_language("nl")
        if content:
            instance.content = content

        return instance


class NestedContentElementSerializer(serializers.ModelSerializer):

    labels = serializers.SlugRelatedField(
        slug_field="naam", queryset=ContentLabel.objects.all(), many=True
    )

    content = serializers.CharField(
        required=True,
        max_length=100,
        help_text=_("De content van dit content element."),
    )

    class Meta:
        model = ContentElement
        fields = (
            "id",
            "content",
            "labels",
        )


class ContentElementTranslationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(
        required=True,
        max_length=100,
        help_text=_("De content van dit content element."),
    )

    class Meta:
        model = ContentElement
        fields = ("id", "content")
