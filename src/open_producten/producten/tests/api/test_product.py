import datetime

from django.urls import reverse
from django.utils.translation import gettext as _

from django_json_schema_model.models import JsonSchema
from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producten.models import Product
from open_producten.producten.tests.factories import ProductFactory
from open_producten.producttypen.tests.factories import ProductTypeFactory
from open_producten.utils.tests.cases import BaseApiTestCase


@freeze_time("2024-01-01")
class TestProduct(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create(toegestane_statussen=["gereed"])
        self.data = {
            "product_type_id": self.product_type.id,
            "bsn": "111222333",
            "data": [],
            "status": "initieel",
        }
        self.path = reverse("product-list")

    def detail_path(self, product):
        return reverse("product-detail", args=[product.id])

    def test_read_product_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "product_type_id": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
            },
        )

    def test_create_product(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        product_type = product.product_type
        expected_data = {
            "id": str(product.id),
            "bsn": product.bsn,
            "kvk": product.kvk,
            "verbruiksobject": None,
            "status": product.status,
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "product_type": {
                "id": str(product_type.id),
                "naam": product_type.naam,
                "code": product_type.code,
                "samenvatting": product_type.samenvatting,
                "beschrijving": product_type.beschrijving,
                "uniforme_product_naam": product_type.uniforme_product_naam.uri,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type.update_datum.astimezone().isoformat(),
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_verbruiksobject(self):
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

        data = self.data | {"verbruiksobject": {"naam": "Test"}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        product_type = product.product_type
        expected_data = {
            "id": str(product.id),
            "bsn": product.bsn,
            "kvk": product.kvk,
            "verbruiksobject": {"naam": "Test"},
            "status": product.status,
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "product_type": {
                "id": str(product_type.id),
                "naam": product_type.naam,
                "code": product_type.code,
                "samenvatting": product_type.samenvatting,
                "beschrijving": product_type.beschrijving,
                "uniforme_product_naam": product_type.uniforme_product_naam.uri,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type.update_datum.astimezone().isoformat(),
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_invalid_verbruiksobject(self):
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

        data = self.data | {"verbruiksobject": {"naam": 123}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "verbruiksobject": [
                    ErrorDetail(
                        string=_(
                            "Het verbruiksobject komt niet overeen met het schema gedefinieerd op het product type."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_without_bsn_or_kvk_returns_error(self):
        data = self.data.copy()
        data.pop("bsn")
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "bsn_or_kvk": [
                    ErrorDetail(
                        string=_(
                            "Een product moet een bsn, kvk nummer of beiden hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )
        self.assertEqual(Product.objects.count(), 0)

    def test_create_product_with_not_allowed_state(self):
        response = self.client.post(self.path, self.data | {"status": "actief"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    ErrorDetail(
                        string=f"Status 'Actief' is niet toegestaan voor het product type {self.product_type.naam}.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_allowed_state(self):
        response = self.client.post(self.path, self.data | {"status": "gereed"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)

    def test_update_product(self):
        product_type = ProductTypeFactory.create(toegestane_statussen=["verlopen"])
        product = ProductFactory.create(bsn="111222333", product_type=product_type)

        data = self.data | {
            "eind_datum": datetime.date(2025, 12, 31),
            "product_type_id": product_type.id,
        }
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().eind_datum, data["eind_datum"])

    def test_update_product_without_bsn_or_kvk(self):
        product = ProductFactory.create(bsn="111222333")

        data = self.data | {"bsn": None}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "bsn_or_kvk": [
                    ErrorDetail(
                        string=_(
                            "Een product moet een bsn, kvk nummer of beiden hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_with_not_allowed_state(self):
        product = ProductFactory.create(bsn="111222333")
        data = self.data.copy() | {"status": "actief"}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    ErrorDetail(
                        string=f"Status 'Actief' is niet toegestaan voor het product type {self.product_type.naam}.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_product(self):
        product = ProductFactory.create(
            bsn="111222333",
            product_type=ProductTypeFactory.create(toegestane_statussen=["verlopen"]),
        )

        data = {"eind_datum": datetime.date(2025, 12, 31)}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().eind_datum, data["eind_datum"])

    def test_read_producten(self):
        product1 = ProductFactory.create(
            bsn="111222333", product_type=self.product_type
        )
        product2 = ProductFactory.create(
            bsn="111222444", product_type=self.product_type
        )

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(product1.id),
                "bsn": product1.bsn,
                "kvk": product1.kvk,
                "verbruiksobject": None,
                "status": product1.status,
                "gepubliceerd": False,
                "start_datum": None,
                "eind_datum": None,
                "aanmaak_datum": product1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product1.update_datum.astimezone().isoformat(),
                "product_type": {
                    "id": str(self.product_type.id),
                    "naam": self.product_type.naam,
                    "code": self.product_type.code,
                    "samenvatting": self.product_type.samenvatting,
                    "beschrijving": self.product_type.beschrijving,
                    "uniforme_product_naam": self.product_type.uniforme_product_naam.uri,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": self.product_type.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.product_type.update_datum.astimezone().isoformat(),
                    "keywords": [],
                },
            },
            {
                "id": str(product2.id),
                "bsn": product2.bsn,
                "kvk": product2.kvk,
                "verbruiksobject": None,
                "status": product2.status,
                "gepubliceerd": False,
                "start_datum": None,
                "eind_datum": None,
                "aanmaak_datum": product2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product2.update_datum.astimezone().isoformat(),
                "product_type": {
                    "id": str(self.product_type.id),
                    "naam": self.product_type.naam,
                    "code": self.product_type.code,
                    "samenvatting": self.product_type.samenvatting,
                    "beschrijving": self.product_type.beschrijving,
                    "uniforme_product_naam": self.product_type.uniforme_product_naam.uri,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": self.product_type.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.product_type.update_datum.astimezone().isoformat(),
                    "keywords": [],
                },
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    @freeze_time("2025-12-31")
    def test_read_product(self):
        product_type = ProductTypeFactory.create(toegestane_statussen=["gereed"])
        product = ProductFactory.create(bsn="111222333", product_type=product_type)

        response = self.client.get(self.detail_path(product))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(product.id),
            "bsn": "111222333",
            "kvk": None,
            "verbruiksobject": None,
            "status": product.status,
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "aanmaak_datum": "2025-12-31T01:00:00+01:00",
            "update_datum": "2025-12-31T01:00:00+01:00",
            "product_type": {
                "id": str(product_type.id),
                "naam": product_type.naam,
                "code": product_type.code,
                "samenvatting": product_type.samenvatting,
                "beschrijving": product_type.beschrijving,
                "uniforme_product_naam": product_type.uniforme_product_naam.uri,
                "toegestane_statussen": ["gereed"],
                "gepubliceerd": True,
                "aanmaak_datum": "2025-12-31T01:00:00+01:00",
                "update_datum": "2025-12-31T01:00:00+01:00",
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_product(self):
        product = ProductFactory.create(bsn="111222333")
        response = self.client.delete(self.detail_path(product))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)
