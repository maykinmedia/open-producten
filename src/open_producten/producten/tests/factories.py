import factory

from ...producttypen.tests.factories import ProductTypeFactory
from ..models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Product
