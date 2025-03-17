import datetime

from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producten.models import Product
from open_producten.producten.tests.factories import ProductFactory
from open_producten.producttypen.tests.factories import (
    JsonSchemaFactory,
    ProductTypeFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


@freeze_time("2024-01-01")
@override_settings(NOTIFICATIONS_DISABLED=True, PRODUCTEN_API_MAJOR_VERSION=0)
class TestProduct(BaseApiTestCase):
    path = reverse_lazy("product-list")

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create(toegestane_statussen=["gereed"])
        self.data = {
            "product_type_id": self.product_type.id,
            "bsn": "111222333",
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "data": [],
        }

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
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "prijs": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "frequentie": [
                    ErrorDetail(string=_("This field is required."), code="required")
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
            "url": f"http://testserver{self.detail_path(product)}",
            "id": str(product.id),
            "bsn": product.bsn,
            "kvk": product.kvk,
            "status": product.status,
            "verbruiksobject": None,
            "dataobject": None,
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "product_type": {
                "id": str(product_type.id),
                "code": product_type.code,
                "uniforme_product_naam": product_type.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type.update_datum.astimezone().isoformat(),
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_verbruiksobject(self):
        json_schema = JsonSchemaFactory.create(
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
            "url": f"http://testserver{self.detail_path(product)}",
            "bsn": product.bsn,
            "kvk": product.kvk,
            "status": product.status,
            "verbruiksobject": {"naam": "Test"},
            "dataobject": None,
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "product_type": {
                "id": str(product_type.id),
                "code": product_type.code,
                "uniforme_product_naam": product_type.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type.update_datum.astimezone().isoformat(),
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_invalid_verbruiksobject(self):
        json_schema = JsonSchemaFactory.create(
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

    def test_create_product_with_dataobject(self):
        json_schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )

        self.product_type.dataobject_schema = json_schema
        self.product_type.save()

        data = self.data | {"dataobject": {"naam": "Test"}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        product_type = product.product_type
        expected_data = {
            "id": str(product.id),
            "url": f"http://testserver{self.detail_path(product)}",
            "bsn": product.bsn,
            "kvk": product.kvk,
            "status": product.status,
            "verbruiksobject": None,
            "dataobject": {"naam": "Test"},
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "product_type": {
                "id": str(product_type.id),
                "code": product_type.code,
                "uniforme_product_naam": product_type.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type.update_datum.astimezone().isoformat(),
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_invalid_dataobject(self):
        json_schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )

        self.product_type.dataobject_schema = json_schema
        self.product_type.save()

        data = self.data | {"dataobject": {"naam": 123}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "dataobject": [
                    ErrorDetail(
                        string="Het dataobject komt niet overeen met het schema gedefinieerd op het product type.",
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
                        string=_(
                            "Status 'Actief' is niet toegestaan voor het product type {}."
                        ).format(self.product_type.naam),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_allowed_state(self):
        response = self.client.post(self.path, self.data | {"status": "gereed"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
                        string=_(
                            "Status 'Actief' is niet toegestaan voor het product type {}."
                        ).format(self.product_type.naam),
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
                "url": f"http://testserver{self.detail_path(product1)}",
                "id": str(product1.id),
                "bsn": product1.bsn,
                "kvk": product1.kvk,
                "status": product1.status,
                "verbruiksobject": None,
                "dataobject": None,
                "gepubliceerd": False,
                "start_datum": None,
                "eind_datum": None,
                "prijs": str(product1.prijs),
                "frequentie": product1.frequentie,
                "aanmaak_datum": product1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product1.update_datum.astimezone().isoformat(),
                "product_type": {
                    "id": str(self.product_type.id),
                    "code": self.product_type.code,
                    "uniforme_product_naam": self.product_type.uniforme_product_naam.naam,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": self.product_type.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.product_type.update_datum.astimezone().isoformat(),
                    "keywords": [],
                },
            },
            {
                "url": f"http://testserver{self.detail_path(product2)}",
                "id": str(product2.id),
                "bsn": product2.bsn,
                "kvk": product2.kvk,
                "status": product2.status,
                "verbruiksobject": None,
                "dataobject": None,
                "gepubliceerd": False,
                "start_datum": None,
                "eind_datum": None,
                "prijs": str(product2.prijs),
                "frequentie": product2.frequentie,
                "aanmaak_datum": product2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product2.update_datum.astimezone().isoformat(),
                "product_type": {
                    "id": str(self.product_type.id),
                    "code": self.product_type.code,
                    "uniforme_product_naam": self.product_type.uniforme_product_naam.naam,
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
            "url": f"http://testserver{self.detail_path(product)}",
            "id": str(product.id),
            "bsn": "111222333",
            "kvk": None,
            "status": product.status,
            "verbruiksobject": None,
            "dataobject": None,
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": "2025-12-31T01:00:00+01:00",
            "update_datum": "2025-12-31T01:00:00+01:00",
            "product_type": {
                "id": str(product_type.id),
                "code": product_type.code,
                "uniforme_product_naam": product_type.uniforme_product_naam.naam,
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

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_not_checked_when_not_changed(self):
        data = {
            "product_type_id": ProductTypeFactory.create(toegestane_statussen=[]).id,
            "status": "gereed",
            "bsn": "111222333",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "frequentie": "eenmalig",
        }

        product = ProductFactory.create(**data)

        response = self.client.put(self.detail_path(product), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @freeze_time("2025-11-30")
    def test_partial_update_state_and_dates_are_not_checked_when_not_changed(self):
        data = {
            "product_type_id": ProductTypeFactory.create(toegestane_statussen=[]).id,
            "status": "gereed",
            "bsn": "111222333",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)

        response = self.client.patch(self.detail_path(product), {"kvk": "12345678"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_checked_when_product_type_is_changed(self):
        new_product_type = ProductTypeFactory.create(toegestane_statussen=[])

        tests = [
            {
                "field": {"status": "gereed"},
                "error": {
                    "status": [
                        ErrorDetail(
                            string=_(
                                "Status 'Gereed' is niet toegestaan voor het product type {}."
                            ).format(new_product_type.naam),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"start_datum": datetime.date(2025, 12, 31)},
                "error": {
                    "start_datum": [
                        ErrorDetail(
                            string=_(
                                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"eind_datum": datetime.date(2026, 12, 31)},
                "error": {
                    "eind_datum": [
                        ErrorDetail(
                            string=_(
                                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het product type."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
        ]

        for test in tests:
            with self.subTest(
                f"Test {test['field']} is checked when product type is changed."
            ):

                data = {
                    "product_type_id": ProductTypeFactory.create(
                        toegestane_statussen=[]
                    ).id,
                    "bsn": "111222333",
                    "prijs": "10",
                    "frequentie": "eenmalig",
                } | test["field"]

                product = ProductFactory.create(**data)

                response = self.client.put(
                    self.detail_path(product),
                    data | {"product_type_id": new_product_type.id},
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(response.data, test["error"])

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_checked_when_changed(self):
        product_type = ProductTypeFactory.create(toegestane_statussen=[])
        tests = [
            {
                "field": {"status": "gereed"},
                "error": {
                    "status": [
                        ErrorDetail(
                            string=_(
                                "Status 'Gereed' is niet toegestaan voor het product type {}."
                            ).format(product_type.naam),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"start_datum": datetime.date(2025, 12, 31)},
                "error": {
                    "start_datum": [
                        ErrorDetail(
                            string=_(
                                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"eind_datum": datetime.date(2026, 12, 31)},
                "error": {
                    "eind_datum": [
                        ErrorDetail(
                            string=_(
                                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het product type."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
        ]

        for test in tests:
            with self.subTest(
                f"Test {test['field']} is checked when product type is changed."
            ):

                data = {
                    "product_type_id": product_type.id,
                    "bsn": "111222333",
                    "status": "initieel",
                    "prijs": "10",
                    "frequentie": "eenmalig",
                }

                product = ProductFactory.create(**data)

                response = self.client.put(
                    self.detail_path(product),
                    data | test["field"],
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(response.data, test["error"])
