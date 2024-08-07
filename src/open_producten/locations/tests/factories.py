import factory

from ..models import Contact, Location, Neighbourhood, Organisation, OrganisationType


class OrganisationTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"organisation type {n}")

    class Meta:
        model = OrganisationType


class NeighbourhoodFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"neighbourhood {n}")

    class Meta:
        model = Neighbourhood


class OrganisationFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"organisation {n}")
    slug = factory.Faker("slug")
    type = factory.SubFactory(OrganisationTypeFactory)
    neighbourhood = factory.SubFactory(NeighbourhoodFactory)

    street = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")
    city = factory.Faker("city", locale="nl_NL")

    class Meta:
        model = Organisation


class LocationFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"location {n}")
    street = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")

    class Meta:
        model = Location


class ContactFactory(factory.django.DjangoModelFactory):
    organisation = factory.SubFactory(OrganisationFactory)
    first_name = factory.Faker("name")
    last_name = factory.Faker("name")
    role = factory.Faker("word")

    class Meta:
        model = Contact
