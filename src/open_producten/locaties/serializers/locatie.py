from rest_framework import serializers

from open_producten.locaties.models import Contact, Locatie, Organisatie


class LocatieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Locatie
        fields = "__all__"


class OrganisatieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisatie
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    organisatie = OrganisatieSerializer(read_only=True)
    organisatie_id = serializers.PrimaryKeyRelatedField(
        queryset=Organisatie.objects.all(), source="organisatie", write_only=True
    )

    class Meta:
        model = Contact
        fields = "__all__"
