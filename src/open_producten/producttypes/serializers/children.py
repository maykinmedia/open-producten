from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import (
    Condition,
    Field,
    File,
    Link,
    Price,
    PriceOption,
    Question,
    Tag,
    TagType,
    UniformProductName,
)


class PriceOptionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = PriceOption
        exclude = ("price",)


class PriceSerializer(serializers.ModelSerializer):
    options = PriceOptionSerializer(many=True, default=[])

    class Meta:
        model = Price
        exclude = ("id", "product_type")

    @transaction.atomic()
    def create(self, validated_data):
        options = validated_data.pop("options")
        product_type = validated_data.pop("product_type")

        price = Price.objects.create(**validated_data, product_type=product_type)

        for option in options:
            PriceOption.objects.create(price=price, **option)

        return price

    @transaction.atomic()
    def update(self, instance, validated_data):
        options = validated_data.pop("options")
        price = super().update(instance, validated_data)
        current_option_ids = list(price.options.values_list("id", flat=True))

        for option in options:
            option_id = option.pop("id", None)
            if option_id is None:
                PriceOption.objects.create(price=price, **option)

            elif option_id in current_option_ids:
                existing_option = PriceOption.objects.get(id=option_id)
                existing_option.amount = option["amount"]
                existing_option.description = option["description"]
                existing_option.save()
                current_option_ids.remove(option_id)

            else:
                raise ValidationError(
                    f"Price option id {option_id} is not part of to price object."
                )

        PriceOption.objects.filter(id__in=current_option_ids).delete()

        return price


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        exclude = ("id", "product_type")


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        exclude = ("id", "product_type")


class TagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagType
        exclude = ("id",)


class TagSerializer(serializers.ModelSerializer):
    type = TagTypeSerializer()

    class Meta:
        model = Tag
        exclude = ("id",)


class UpnSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniformProductName
        exclude = ("id",)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ("id", "category", "product_type")


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        exclude = ("id",)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        exclude = ("id", "product_type")
