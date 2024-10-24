from django.contrib.gis.geos import Point

import factory
from faker.providers import BaseProvider

from ..models import Contact, Location, Neighbourhood, Organisation, OrganisationType


class DjangoGeoPointProvider(BaseProvider):

    def geo_point(self, **kwargs):
        kwargs["coords_only"] = True
        # # generate() is not working in later Faker versions
        # faker = factory.Faker('local_latlng', **kwargs)
        # coords = faker.generate()
        faker = factory.faker.faker.Faker()
        coords = faker.local_latlng(**kwargs)
        return Point(x=float(coords[1]), y=float(coords[0]))


class OrganisationTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"organisation type {n}")

    class Meta:
        model = OrganisationType


class NeighbourhoodFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"neighbourhood {n}")

    class Meta:
        model = Neighbourhood


class OrganisationFactory(factory.django.DjangoModelFactory):
    factory.Faker.add_provider(DjangoGeoPointProvider)

    name = factory.Sequence(lambda n: f"organisation {n}")
    type = factory.SubFactory(OrganisationTypeFactory)
    neighbourhood = factory.SubFactory(NeighbourhoodFactory)

    street = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")
    city = factory.Faker("city", locale="nl_NL")
    coordinates = factory.Faker("geo_point", country_code="NL")

    class Meta:
        model = Organisation


class LocationFactory(factory.django.DjangoModelFactory):
    factory.Faker.add_provider(DjangoGeoPointProvider)

    name = factory.Sequence(lambda n: f"location {n}")
    street = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")
    coordinates = factory.Faker("geo_point", country_code="NL")

    class Meta:
        model = Location


class ContactFactory(factory.django.DjangoModelFactory):
    organisation = factory.SubFactory(OrganisationFactory)
    first_name = factory.Faker("name")
    last_name = factory.Faker("name")
    role = factory.Faker("word")

    class Meta:
        model = Contact
