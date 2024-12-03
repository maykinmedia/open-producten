from django.core.exceptions import ValidationError

from rest_framework import serializers

from open_producten.producttypen.models import Onderwerp, ProductType, Vraag
from open_producten.utils.serializers import model_to_dict_with_related_ids


class VraagSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all(), required=False
    )
    onderwerp_id = serializers.PrimaryKeyRelatedField(
        source="onderwerp", queryset=Onderwerp.objects.all(), required=False
    )

    class Meta:
        model = Vraag
        exclude = ("product_type", "onderwerp")

    def validate(self, attrs):

        if self.partial:
            all_attrs = model_to_dict_with_related_ids(self.instance) | attrs
        else:
            all_attrs = attrs

        instance = Vraag(**all_attrs)

        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError({"product_type_onderwerp": e.message})

        return attrs
