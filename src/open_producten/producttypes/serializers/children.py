from django.db import transaction

from rest_framework import serializers

from open_producten.utils.serializers import model_to_dict_with_related_ids

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
        exclude = ("product_type",)

    def validate_options(self, options: list[PriceOption]) -> list[PriceOption]:
        if len(options) == 0:
            raise serializers.ValidationError("At least one option is required")
        return options

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
        options = validated_data.pop("options", None)
        price = super().update(instance, validated_data)
        option_errors = []

        if options is not None:
            current_option_ids = set(
                price.options.values_list("id", flat=True).distinct()
            )
            seen_option_ids = set()
            for idx, option in enumerate(options):
                option_id = option.pop("id", None)
                if option_id is None:
                    PriceOption.objects.create(price=price, **option)

                elif option_id in current_option_ids:

                    if option_id in seen_option_ids:
                        option_errors.append(
                            f"Duplicate option id {option_id} at index {idx}"
                        )
                    seen_option_ids.add(option_id)

                    existing_option = PriceOption.objects.get(id=option_id)
                    existing_option.amount = option["amount"]
                    existing_option.description = option["description"]
                    existing_option.save()

                else:
                    try:
                        PriceOption.objects.get(id=option_id)
                        option_errors.append(
                            f"Price option id {option_id} at index {idx} is not part of price object"
                        )
                    except PriceOption.DoesNotExist:
                        option_errors.append(
                            f"Price option id {option_id} at index {idx} does not exist"
                        )

            if option_errors:
                raise serializers.ValidationError({"options": option_errors})

            PriceOption.objects.filter(
                id__in=(current_option_ids - seen_option_ids)
            ).delete()

        return price


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        exclude = ("product_type",)

    def validate(self, attrs):
        if self.partial:
            all_attrs = model_to_dict_with_related_ids(self.instance) | attrs
        else:
            all_attrs = attrs

        instance = Field(**all_attrs)
        instance.clean()
        return attrs


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        exclude = ("product_type",)


class TagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagType
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    type = TagTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=TagType.objects.all(), source="type"
    )

    class Meta:
        model = Tag
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ("category", "product_type")


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = "__all__"


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        exclude = ("product_type",)
