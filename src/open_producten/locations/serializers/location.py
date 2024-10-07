from rest_framework import serializers

from open_producten.locations.models import (
    Contact,
    Location,
    Neighbourhood,
    Organisation,
    OrganisationType,
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class NeighbourhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighbourhood
        fields = "__all__"


class OrganisationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationType
        fields = "__all__"


class OrganisationSerializer(serializers.ModelSerializer):
    neighbourhood = NeighbourhoodSerializer(read_only=True)
    type = OrganisationTypeSerializer(read_only=True)

    neighbourhood_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Neighbourhood.objects.all(), source="neighbourhood"
    )

    type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=OrganisationType.objects.all(), source="type"
    )

    class Meta:
        model = Organisation
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    organisation = OrganisationSerializer(read_only=True)
    organisation_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Organisation.objects.all(), source="organisation"
    )

    class Meta:
        model = Contact
        fields = "__all__"
