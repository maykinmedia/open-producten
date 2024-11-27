import factory

from ...producttypen.tests.factories import ProductTypeFactory
from ..models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    start_datum = factory.Faker("date")
    eind_datum = factory.Faker("date")

    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Product
