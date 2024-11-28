from rest_framework import serializers

from open_producten.locaties.models import Contact, Locatie, Organisatie


class LocatieSerializer(serializers.ModelSerializer):
    coordinaten = serializers.SerializerMethodField()

    class Meta:
        model = Locatie
        fields = "__all__"

    def get_coordinaten(self, obj) -> list:
        return obj.coordinaten.coords

    def create(self, validated_data: dict) -> Locatie:
        locatie = Locatie(**validated_data)
        locatie.clean()
        locatie.save()
        return locatie

    def update(self, instance, validated_data: dict) -> Locatie:
        locatie = super().update(instance, validated_data)
        locatie.clean()
        locatie.save()
        return locatie


class OrganisatieSerializer(serializers.ModelSerializer):
    coordinaten = serializers.SerializerMethodField()

    class Meta:
        model = Organisatie
        fields = "__all__"

    def get_coordinaten(self, obj) -> list:
        return obj.coordinaten.coords

    def create(self, validated_data: dict) -> Organisatie:
        organisatie = Organisatie(**validated_data)
        organisatie.clean()
        organisatie.save()
        return organisatie

    def update(self, instance, validated_data: dict) -> Organisatie:
        organisatie = super().update(instance, validated_data)
        organisatie.clean()
        organisatie.save()
        return organisatie


class ContactSerializer(serializers.ModelSerializer):
    organisatie = OrganisatieSerializer(read_only=True)
    organisatie_id = serializers.PrimaryKeyRelatedField(
        queryset=Organisatie.objects.all(), source="organisatie", write_only=True
    )

    class Meta:
        model = Contact
        fields = "__all__"
