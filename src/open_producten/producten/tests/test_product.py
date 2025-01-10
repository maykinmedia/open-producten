from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from freezegun import freeze_time

from open_producten.producttypen.tests.factories import ProductTypeFactory

from ...producttypen.models.producttype import ProductStateChoices
from .factories import ProductFactory


class TestProduct(TestCase):

    def setUp(self):
        self.product_type = ProductTypeFactory.create(toegestane_statussen=["gereed"])

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

    def test_status_part_of_product_type(self):
        product = ProductFactory.build(
            product_type=self.product_type, status="actief", bsn="111222333"
        )

        with self.assertRaisesMessage(
            ValidationError,
            _("Status 'Actief' is niet toegestaan voor het product type {}.").format(self.product_type.naam),
        ):
            product.clean()

    def test_start_datum_is_not_allowed_when_actief_is_not_allowed(self):

        product = ProductFactory.build(
            start_datum=date(2025, 1, 12),
            product_type=self.product_type,
            bsn="111222333",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type.",
        ):
            product.clean()

    def test_eind_datum_is_not_allowed_when_verlopen_is_not_allowed(self):

        product = ProductFactory.build(
            start_datum=date(2025, 1, 12),
            product_type=self.product_type,
            bsn="111222333",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type.",
        ):
            product.clean()

    def test_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        product = ProductFactory.build(
            start_datum=date(2025, 1, 12),
            eind_datum=date(2025, 1, 12),
            product_type=self.product_type,
            bsn="111222333",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "De start datum en eind_datum van een product mogen niet op dezelfde dag vallen.",
        ):
            product.clean()

    def test_start_and_eind_datum_are_not_allowed_to_be_null(self):
        product = ProductFactory.build(
            product_type=self.product_type,
            bsn="111222333",
        )
        product.clean()


@freeze_time("2024-1-1")
class TestProductStateTask(TestCase):
    def setUp(self):
        self.product_type = ProductTypeFactory.create(toegestane_statussen=["actief"])

    def test_product_status_is_set_to_active_on_start_datum(self):
        product = ProductFactory.create(
            status="initieel",
            product_type=self.product_type,
            start_datum=date(2024, 1, 1),
        )

        product.handle_start_datum()

        self.assertEqual(product.status, "actief")

    def test_product_status_is_set_to_active_on_earlier_date(self):
        product = ProductFactory.create(
            status="initieel",
            product_type=self.product_type,
            start_datum=date(2023, 12, 31),
        )

        product.handle_start_datum()

        self.assertEqual(product.status, "actief")

    def test_product_status_is_not_set_to_active_on_later_date(self):
        product = ProductFactory.create(
            status="initieel",
            product_type=self.product_type,
            start_datum=date(2024, 10, 1),
        )

        product.handle_start_datum()

        self.assertEqual(product.status, "initieel")

    def test_product_status_is_not_set_to_active_on_later_states(self):

        for state in [
            ProductStateChoices.ACTIEF,
            ProductStateChoices.VERLOPEN,
            ProductStateChoices.GEWEIGERD,
            ProductStateChoices.INGETROKKEN,
        ]:
            with self.subTest():
                product = ProductFactory.create(
                    status=state.value,
                    product_type=self.product_type,
                    start_datum=date(2024, 1, 1),
                )
                product.handle_start_datum()
                self.assertEqual(product.status, state.value)

    def test_product_status_is_set_to_verlopen_on_eind_datum(self):
        product = ProductFactory.create(
            status="actief", product_type=self.product_type, eind_datum=date(2024, 1, 1)
        )

        product.handle_eind_datum()

        self.assertEqual(product.status, "verlopen")

    def test_product_status_is_set_to_verlopen_on_earlier_date(self):
        product = ProductFactory.create(
            status="actief",
            product_type=self.product_type,
            eind_datum=date(2023, 12, 31),
        )

        product.handle_eind_datum()

        self.assertEqual(product.status, "verlopen")

    def test_product_status_is_not_set_to_verlopen_on_later_date(self):
        product = ProductFactory.create(
            status="actief",
            product_type=self.product_type,
            eind_datum=date(2024, 10, 1),
        )

        product.handle_eind_datum()

        self.assertEqual(product.status, "actief")

    def test_product_status_is_not_set_to_verlopen_on_later_states(self):

        for state in [
            ProductStateChoices.VERLOPEN,
            ProductStateChoices.GEWEIGERD,
            ProductStateChoices.INGETROKKEN,
        ]:
            with self.subTest():
                product = ProductFactory.create(
                    status=state.value,
                    product_type=self.product_type,
                    eind_datum=date(2024, 1, 1),
                )
                product.handle_eind_datum()
                self.assertEqual(product.status, state.value)
