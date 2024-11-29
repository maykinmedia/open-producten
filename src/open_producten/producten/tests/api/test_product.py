import datetime

from freezegun import freeze_time
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producten.models import Product
from open_producten.producten.tests.factories import ProductFactory
from open_producten.producttypen.tests.factories import ProductTypeFactory
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id


def product_to_dict(product):
    product_dict = model_to_dict_with_id(product)
    product_dict["start_datum"] = str(product_dict["start_datum"])
    product_dict["eind_datum"] = str(product_dict["eind_datum"])
    product_dict["aanmaak_datum"] = str(product.aanmaak_datum.astimezone().isoformat())
    product_dict["update_datum"] = str(product.update_datum.astimezone().isoformat())

    product_dict["product_type"] = model_to_dict_with_id(
        product.product_type,
        exclude=(
            "onderwerpen",
            "contacten",
            "locaties",
            "organisaties",
        ),
    )
    product_dict["product_type"][
        "uniforme_product_naam"
    ] = product.product_type.uniforme_product_naam.uri

    product_dict["product_type"]["aanmaak_datum"] = str(
        product.product_type.aanmaak_datum.astimezone().isoformat()
    )
    product_dict["product_type"]["update_datum"] = str(
        product.product_type.update_datum.astimezone().isoformat()
    )
    return product_dict


@freeze_time("2024-01-01")
class TestProduct(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.data = {
            "product_type_id": self.product_type.id,
            "bsn": "111222333",
            "start_datum": datetime.date(2024, 1, 2),
            "eind_datum": datetime.date(2024, 12, 31),
            "data": [],
        }
        self.path = "/api/v1/producten/"

    def test_read_product_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def _create_product(self):
        return ProductFactory.create(bsn="111222333")

    def test_create_product(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(response.data, product_to_dict(product))

    def test_create_product_without_bsn_or_kvk_returns_error(self):
        data = self.data.copy()
        data.pop("bsn")
        response = self.post(data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "bsn_or_kvk": [
                    ErrorDetail(
                        string="Een product moet een bsn, kvk nummer of beiden hebben.",
                        code="invalid",
                    )
                ]
            },
        )
        self.assertEqual(Product.objects.count(), 0)

    def test_update_product(self):
        product = self._create_product()

        data = self.data | {"eind_datum": datetime.date(2025, 12, 31)}
        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().eind_datum, data["eind_datum"])

    def test_update_product_without_bsn_or_kvk(self):
        product = self._create_product()

        data = self.data.copy()
        data.pop("bsn")
        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "bsn_or_kvk": [
                    ErrorDetail(
                        string="Een product moet een bsn, kvk nummer of beiden hebben.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_product(self):
        product = self._create_product()

        data = {"eind_datum": datetime.date(2025, 12, 31)}
        response = self.patch(product.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)

    def test_read_producten(self):
        product = self._create_product()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [product_to_dict(product)])

    def test_read_product(self):
        product = self._create_product()

        response = self.get(product.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_to_dict(product))

    def test_delete_product(self):
        product = self._create_product()
        response = self.delete(product.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)
