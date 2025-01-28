import datetime
from unittest.mock import patch

from django.test import TestCase

from open_producten.producttypen.tests.factories import ProductTypeFactory

from ..admin.product import ProductAdminForm
from .factories import ProductFactory


class TestProductAdminForm(TestCase):
    def setUp(self):
        self.data = {"status"}

    def test_status_and_dates_are_not_validated_when_not_changed(self):
        data = {
            "product_type": ProductTypeFactory.create(toegestane_statussen=[]),
            "status": "gereed",
            "bsn": "111222333",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()

    @patch("open_producten.producten.admin.product.validate_status")
    @patch("open_producten.producten.admin.product.validate_start_datum")
    @patch("open_producten.producten.admin.product.validate_eind_datum")
    def test_status_and_dates_are_validated_when_changed(
        self, mock_validate_status, mock_validate_start_datum, mock_validate_eind_datum
    ):
        data = {
            "product_type": ProductTypeFactory.create(toegestane_statussen=["gereed"]),
            "status": "initeel",
            "bsn": "111222333",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        data["status"] = "gereed"
        data["start_datum"] = datetime.date(2025, 11, 30)
        data["eind_datum"] = datetime.date(2026, 11, 30)
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()
        mock_validate_status.assert_called_once()
        mock_validate_start_datum.assert_called_once()
        mock_validate_eind_datum.assert_called_once()

    @patch("open_producten.producten.admin.product.validate_status")
    @patch("open_producten.producten.admin.product.validate_start_datum")
    @patch("open_producten.producten.admin.product.validate_eind_datum")
    def test_status__and_dates_are_validated_when_product_type_is_changed(
        self, mock_validate_status, mock_validate_start_datum, mock_validate_eind_datum
    ):
        data = {
            "product_type": ProductTypeFactory.create(toegestane_statussen=["gereed"]),
            "status": "gereed",
            "bsn": "111222333",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)
        data["product_type"] = ProductTypeFactory.create(toegestane_statussen=[]).id
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()
        mock_validate_status.assert_called_once()
        mock_validate_start_datum.assert_called_once()
        mock_validate_eind_datum.assert_called_once()
