import factory

from ...producttypes.tests.factories import ProductTypeFactory
from ..models import Data, Product


class ProductFactory(factory.django.DjangoModelFactory):
    start_date = factory.Faker("date")
    end_date = factory.Faker("date")

    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Product


class DataFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Data
