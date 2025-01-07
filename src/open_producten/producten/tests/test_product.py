from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from django_json_schema.models import JsonSchema

from open_producten.producttypen.tests.factories import ProductTypeFactory

from .factories import ProductFactory


class TestProduct(TestCase):

    def setUp(self):
        self.product_type = ProductTypeFactory.create()

    def test_bsn_validation_raises_on_invalid_value(self):
        invalid_values = [
            "123",  # min length
            "12345678910",  # max length
            "abcdefghi",  # regex
            "192837465",  # 11 check
        ]
        for value in invalid_values:
            with self.subTest(f"{value} should raise an error"):
                with self.assertRaises(ValidationError):
                    ProductFactory.build(
                        bsn=value, product_type=self.product_type
                    ).full_clean()

    def test_bsn_validation_validates_on_valid_value(self):
        ProductFactory.build(
            bsn="111222333", product_type=self.product_type
        ).full_clean()

    def test_kvk_validation_raises_on_invalid_value(self):
        invalid_values = [
            "1234",  # min length
            "123456789",  # max length
            "test",  # regex
        ]
        for value in invalid_values:
            with self.subTest(f"{value} should raise an error"):
                with self.assertRaises(ValidationError):
                    ProductFactory.build(
                        kvk=value, product_type=self.product_type
                    ).full_clean()

    def test_kvk_validation_validates_on_valid_value(self):
        ProductFactory.build(
            kvk="11122333", product_type=self.product_type
        ).full_clean()

    def test_bsn_or_kvk_required(self):
        product = ProductFactory.build(product_type=self.product_type)

        with self.assertRaisesMessage(
            ValidationError, _("Een product moet een bsn, kvk nummer of beiden hebben.")
        ):
            product.clean()

        ProductFactory.build(
            bsn="111222333", product_type=self.product_type
        ).full_clean()
        ProductFactory.build(
            kvk="11122233", product_type=self.product_type
        ).full_clean()

    def test_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        product = ProductFactory.build(
            start_datum=date(2025, 1, 12),
            eind_datum=date(2025, 1, 12),
            product_type=self.product_type,
            bsn="111222333",
        )

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "De start datum en eind_datum van een product mogen niet op dezelfde dag vallen."
            ),
        ):
            product.clean()

    def test_start_and_eind_datum_are_not_allowed_to_be_null(self):
        product = ProductFactory.build(
            product_type=self.product_type,
            bsn="111222333",
        )
        product.clean()

    def test_verbruiksobject_is_valid(self):
        json_schema = JsonSchema.objects.create(
            name="json-schema",
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )
        self.product_type.verbruiksobject_schema = json_schema
        self.product_type.save()

        product = ProductFactory.build(
            kvk="11122333",
            product_type=self.product_type,
            verbruiksobject={"naam": "test"},
        )

        product.clean()

    def test_verbruiksobject_is_invalid(self):
        json_schema = JsonSchema.objects.create(
            name="json-schema",
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )
        self.product_type.verbruiksobject_schema = json_schema
        self.product_type.save()

        product = ProductFactory.build(
            kvk="11122333",
            product_type=self.product_type,
            verbruiksobject={"naam": 1234},
        )

        with self.assertRaisesMessage(
            ValidationError,
            _("Het verbruiksobject komt niet overeen met het schema gedefinieerd op het product type."),
        ):
            product.clean()

    def test_verbruiksobject_without_schema(self):
        product = ProductFactory.build(
            kvk="11122333",
            product_type=self.product_type,
            verbruiksobject={"naam": 1234},
        )

        product.clean()

    def test_verbruiksobject_with_schema_without_object(self):
        json_schema = JsonSchema.objects.create(
            name="json-schema",
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )
        self.product_type.verbruiksobject_schema = json_schema
        self.product_type.save()

        product = ProductFactory.build(
            kvk="11122333",
            product_type=self.product_type,
        )

        product.clean()
