from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.test import TestCase

from open_producten.core.test_helpers import build_formset_data
from open_producten.products.models import Product
from open_producten.producttypes.models import FieldTypes
from open_producten.producttypes.tests.factories import FieldFactory, ProductTypeFactory

from ..admin.data import DataInlineFormSet
from ..models import Data
from .factories import ProductFactory


class TestDataInline(TestCase):

    def setUp(self):
        self.product_type = ProductTypeFactory.create()

        self.formset = inlineformset_factory(
            Product, Data, formset=DataInlineFormSet, fields="__all__"
        )

    def test_no_data_no_field(self):
        product = ProductFactory.build(product_type=self.product_type)

        data = build_formset_data(self.product_type.id, "data")

        object_formset = self.formset(data, instance=product)
        object_formset.clean()

    def test_no_data_no_required_field(self):
        product = ProductFactory.build(product_type=self.product_type)
        FieldFactory.create(product_type=self.product_type, type=FieldTypes.TEXTFIELD)

        data = build_formset_data(self.product_type.id, "data")

        object_formset = self.formset(data, instance=product)
        object_formset.clean()

    def test_no_data_required_field(self):
        product = ProductFactory.build(product_type=self.product_type)

        FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )

        data = build_formset_data(
            self.product_type.id,
            "data",
        )

        object_formset = self.formset(data, instance=product)

        with self.assertRaises(ValidationError):
            object_formset.clean()

    def test_data_of_required_field(self):
        product = ProductFactory.build(product_type=self.product_type)

        text_field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )

        data = build_formset_data(
            self.product_type.id,
            "data",
            {
                "id": "",
                "product": product.id,
                "field": text_field.id,
                "data": "test",
            },
        )

        object_formset = self.formset(data, instance=product)
        object_formset.clean()

    def test_field_not_part_of_type(self):
        product = ProductFactory.build(product_type=self.product_type)

        postal_field = FieldFactory.create(type=FieldTypes.POSTCODE)

        data = build_formset_data(
            self.product_type.id,
            "data",
            {
                "id": "",
                "product": product.id,
                "field": postal_field.id,
                "data": "1234 AA",
            },
        )

        object_formset = self.formset(data, instance=product)

        with self.assertRaises(ValidationError):
            object_formset.clean()
