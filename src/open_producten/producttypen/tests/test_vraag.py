from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import ProductTypeFactory, ThemaFactory, VraagFactory


class TestVraag(TestCase):

    def setUp(self):
        self.productType = ProductTypeFactory.create()
        self.thema = ThemaFactory.create()

    def test_error_when_linked_to_product_type_and_thema(self):
        vraag = VraagFactory.build(product_type=self.productType, thema=self.thema)

        with self.assertRaisesMessage(
            ValidationError,
            "Een vraag kan niet gelink zijn aan een thema en een product type.",
        ):
            vraag.clean()

    def test_error_when_not_linked_to_product_type_or_thema(self):
        vraag = VraagFactory.build()

        with self.assertRaisesMessage(
            ValidationError,
            "Een vraag moet gelinkt zijn aan een thema of een product type.",
        ):
            vraag.clean()
