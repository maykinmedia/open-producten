import factory.fuzzy

from ..models import (
    Bestand,
    Eigenschap,
    ExterneCode,
    Link,
    Prijs,
    PrijsOptie,
    ProductType,
    Thema,
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
    code = factory.Sequence(lambda n: f"product type code {n}")
    gepubliceerd = True
    uniforme_product_naam = factory.SubFactory(UniformeProductNaamFactory)

    class Meta:
        model = ProductType


class ThemaFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"thema {n}")
    beschrijving = factory.Faker("sentence")
    gepubliceerd = True

    class Meta:
        model = Thema


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


class EigenschapFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"key {n}")
    waarde = factory.Faker("word")

    class Meta:
        model = Eigenschap


class ExterneCodeFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"systeem {n}")
    code = factory.Faker("word")

    class Meta:
        model = ExterneCode
