from django.core.exceptions import ValidationError
from django.test import TestCase

from open_producten.producttypes.tests.factories import ProductTypeFactory

from .factories import ProductFactory


class TestProduct(TestCase):

    def setUp(self):
        self.product_type = ProductTypeFactory.create()

    def test_bsn_validation(self):
        # min length
        product = ProductFactory.build(bsn="123", product_type=self.product_type)
        with self.assertRaises(ValidationError):
            product.full_clean()

        # max length
        product = ProductFactory.build(
            bsn="12345678910", product_type=self.product_type
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

        # regex
        product = ProductFactory.build(bsn="abcdefghi", product_type=self.product_type)
        with self.assertRaises(ValidationError):
            product.full_clean()

        # 11 check
        product = ProductFactory.build(bsn="192837465", product_type=self.product_type)
        with self.assertRaises(ValidationError):
            product.full_clean()

        ProductFactory.build(
            bsn="111222333", product_type=self.product_type
        ).full_clean()

    def test_kvk_validation(self):
        # min length
        product = ProductFactory.build(kvk="1234", product_type=self.product_type)
        with self.assertRaises(ValidationError):
            product.full_clean()

        # max length
        product = ProductFactory.build(kvk="123456789", product_type=self.product_type)
        with self.assertRaises(ValidationError):
            product.full_clean()

        # regex
        product = ProductFactory.build(kvk="test", product_type=self.product_type)
        with self.assertRaises(ValidationError):
            product.full_clean()

        ProductFactory.build(
            kvk="11122333", product_type=self.product_type
        ).full_clean()

    def test_bsn_or_kvk_required(self):
        product = ProductFactory.build(product_type=self.product_type)

        with self.assertRaises(ValidationError):
            product.clean()

        ProductFactory.build(
            bsn="111222333", product_type=self.product_type
        ).full_clean()
        ProductFactory.build(
            kvk="11122233", product_type=self.product_type
        ).full_clean()
