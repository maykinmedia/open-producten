from django.contrib.gis.geos import Point

import factory
from faker.providers import BaseProvider

from ..models import Contact, Locatie, Organisatie


class DjangoGeoPointProvider(BaseProvider):

    def geo_point(self, **kwargs):
        kwargs["coords_only"] = True
        faker = factory.faker.faker.Faker()
        coords = faker.local_latlng(**kwargs)
        return Point(x=float(coords[1]), y=float(coords[0]))


class OrganisatieFactory(factory.django.DjangoModelFactory):
    factory.Faker.add_provider(DjangoGeoPointProvider)

    naam = factory.Sequence(lambda n: f"organisatie {n}")

    straat = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")
    stad = factory.Faker("city", locale="nl_NL")
    coordinaten = factory.Faker("geo_point", country_code="NL")

    class Meta:
        model = Organisatie


class LocatieFactory(factory.django.DjangoModelFactory):
    factory.Faker.add_provider(DjangoGeoPointProvider)

    naam = factory.Sequence(lambda n: f"locatie {n}")
    straat = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")
    coordinaten = factory.Faker("geo_point", country_code="NL")

    class Meta:
        model = Locatie


class ContactFactory(factory.django.DjangoModelFactory):
    organisatie = factory.SubFactory(OrganisatieFactory)
    voornaam = factory.Faker("name")
    achternaam = factory.Faker("name")
    rol = factory.Faker("word")

    class Meta:
        model = Contact
