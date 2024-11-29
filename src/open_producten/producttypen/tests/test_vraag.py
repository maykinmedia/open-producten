from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import OnderwerpFactory, ProductTypeFactory, VraagFactory


class TestVraag(TestCase):

    def setUp(self):
        self.productType = ProductTypeFactory.create()
        self.onderwerp = OnderwerpFactory.create()

    def test_error_when_linked_to_product_type_and_onderwerp(self):
        vraag = VraagFactory.build(
            product_type=self.productType, onderwerp=self.onderwerp
        )

        with self.assertRaises(ValidationError):
            vraag.clean()

    def test_error_when_not_linked_to_product_type_or_onderwerp(self):
        vraag = VraagFactory.build()

        with self.assertRaises(ValidationError):
            vraag.clean()
