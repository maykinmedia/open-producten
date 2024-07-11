from datetime import date

from django.test import TestCase

from freezegun import freeze_time

from .factories import PriceFactory, ProductTypeFactory


class TestProductType(TestCase):
    def setUp(self):
        self.product_type = ProductTypeFactory.create()
        self.past_price = PriceFactory.create(
            product_type=self.product_type, valid_from=date(2020, 1, 1)
        )
        self.present_price = PriceFactory.create(
            product_type=self.product_type, valid_from=date(2024, 1, 1)
        )
        self.future_price = PriceFactory.create(
            product_type=self.product_type, valid_from=date(2025, 1, 1)
        )

    @freeze_time("2024-02-02")
    def test_current_price(self):
        price = self.product_type.current_price
        self.assertEqual(price, self.present_price)

    def test_current_price_without_prices(self):
        self.product_type = ProductTypeFactory.create()
        self.assertIsNone(self.product_type.current_price)
