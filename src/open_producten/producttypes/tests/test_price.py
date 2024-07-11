from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import PriceFactory, PriceOptionFactory, ProductTypeFactory


class TestPrice(TestCase):

    def test_unique(self):
        product_type = ProductTypeFactory.create()
        PriceFactory.create(
            product_type=product_type, valid_from=date.today() + timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            duplicate = PriceFactory.build(
                product_type=product_type, valid_from=date.today() + timedelta(days=1)
            )
            duplicate.full_clean()

    def test_min_date(self):
        with self.assertRaises(ValidationError):
            price = PriceFactory.build(valid_from=date(2020, 1, 1))
            price.full_clean()


class TestPriceOption(TestCase):
    def setUp(self):
        self.price = PriceFactory.create()

    def test_min_amount(self):
        with self.assertRaises(ValidationError):
            option = PriceOptionFactory.build(price=self.price, amount=Decimal("-1"))
            option.full_clean()

    def test_decimal_places(self):
        with self.assertRaises(ValidationError):
            option = PriceOptionFactory.build(price=self.price, amount=Decimal("0.001"))
            option.full_clean()
