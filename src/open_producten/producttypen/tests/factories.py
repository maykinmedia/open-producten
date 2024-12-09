import factory.fuzzy

from ..models import (
    Bestand,
    Link,
    Onderwerp,
    Prijs,
    PrijsOptie,
    ProductType,
    UniformeProductNaam,
    Vraag,
)


class UniformeProductNaamFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"upn {n}")
    uri = factory.Faker("url")

    class Meta:
        model = UniformeProductNaam


class ProductTypeFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"product type {n}")
    samenvatting = factory.Faker("sentence")
    beschrijving = factory.Faker("paragraph")
    gepubliceerd = True
    uniforme_product_naam = factory.SubFactory(UniformeProductNaamFactory)

    class Meta:
        model = ProductType


class OnderwerpFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"onderwerp {n}")
    beschrijving = factory.Faker("sentence")
    gepubliceerd = True

    class Meta:
        model = Onderwerp

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """For now factory creates only root onderwerpen"""
        return Onderwerp.add_root(**kwargs)


class VraagFactory(factory.django.DjangoModelFactory):
    vraag = factory.Faker("sentence")
    antwoord = factory.Faker("text")

    class Meta:
        model = Vraag


class PrijsFactory(factory.django.DjangoModelFactory):
    actief_vanaf = factory.Faker("date")
    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Prijs


class PrijsOptieFactory(factory.django.DjangoModelFactory):
    beschrijving = factory.Faker("sentence")
    bedrag = factory.fuzzy.FuzzyDecimal(1, 10)

    class Meta:
        model = PrijsOptie


class BestandFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    bestand = factory.django.FileField(filename="test_bestand.txt")

    class Meta:
        model = Bestand


class LinkFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"link {n}")
    url = factory.Faker("url")

    class Meta:
        model = Link
