import factory

from ...producttypen.tests.factories import ProductTypeFactory
from ..models import Product
from ..models.product import PrijsFrequentieChoices


class ProductFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    prijs = factory.fuzzy.FuzzyDecimal(1, 10)
    frequentie = factory.fuzzy.FuzzyChoice(
        [x[0] for x in PrijsFrequentieChoices.choices]
    )

    class Meta:
        model = Product
