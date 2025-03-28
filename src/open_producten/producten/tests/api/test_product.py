import datetime
import uuid

from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producten.models import Eigenaar, Product
from open_producten.producten.tests.factories import EigenaarFactory, ProductFactory
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
        self.producttype = ProductTypeFactory.create(toegestane_statussen=["gereed"])
        self.data = {
            "producttype_id": self.producttype.id,
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "eigenaren": [{"kvk_nummer": "12345678"}],
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
                "producttype_id": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "prijs": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "frequentie": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "eigenaren": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
            },
        )

    def test_create_product(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        producttype = product.producttype
        expected_data = {
            "url": f"http://testserver{self.detail_path(product)}",
            "id": str(product.id),
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
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "id": str(product.eigenaren.get().id),
                }
            ],
            "producttype": {
                "id": str(producttype.id),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
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

        self.producttype.verbruiksobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"verbruiksobject": {"naam": "Test"}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        producttype = product.producttype
        expected_data = {
            "id": str(product.id),
            "url": f"http://testserver{self.detail_path(product)}",
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
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "id": str(product.eigenaren.get().id),
                }
            ],
            "producttype": {
                "id": str(producttype.id),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
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

        self.producttype.verbruiksobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"verbruiksobject": {"naam": 123}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "verbruiksobject": [
                    ErrorDetail(
                        string=_(
                            "Het verbruiksobject komt niet overeen met het schema gedefinieerd op het producttype."
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

        self.producttype.dataobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"dataobject": {"naam": "Test"}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        producttype = product.producttype
        expected_data = {
            "id": str(product.id),
            "url": f"http://testserver{self.detail_path(product)}",
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
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "id": str(product.eigenaren.get().id),
                }
            ],
            "producttype": {
                "id": str(producttype.id),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
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

        self.producttype.dataobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"dataobject": {"naam": 123}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "dataobject": [
                    ErrorDetail(
                        string="Het dataobject komt niet overeen met het schema gedefinieerd op het producttype.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_not_allowed_state(self):
        data = self.data | {"status": "actief"}
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    ErrorDetail(
                        string=_(
                            "Status 'Actief' is niet toegestaan voor het producttype {}."
                        ).format(self.producttype.naam),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_allowed_state(self):
        data = self.data | {"status": "gereed"}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_with_eigenaren(self):
        data = self.data | {
            "eigenaren": [
                {"bsn": "111222333"},
                {"kvk_nummer": "11122233"},
                {"klantnummer": "123"},
            ]
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 3)

    def test_create_product_with_eigenaar_with_id(self):
        id = uuid.uuid4()
        data = self.data | {
            "eigenaren": [
                {"id": id, "kvk_nummer": "11122233"},
            ]
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 1)
        self.assertNotEqual(Eigenaar.objects.get().id, id)

    def test_create_product_with_empty_eigenaar(self):
        data = self.data | {"eigenaren": [{}]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenaren": [
                    {
                        "model_errors": [
                            ErrorDetail(
                                string=_(
                                    "Een eigenaar moet een bsn (en/of klantnummer) of een kvk nummer (met of zonder vestigingsnummer) hebben."
                                ),
                                code="invalid",
                            )
                        ]
                    }
                ]
            },
        )

    def test_create_product_with_vestigingsnummer_only(self):
        data = self.data | {"eigenaren": [{"vestigingsnummer": "123"}]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenaren": [
                    {
                        "vestigingsnummer": [
                            ErrorDetail(
                                string="Een vestigingsnummer kan alleen in combinatie met een kvk nummer worden ingevuld.",
                                code="invalid",
                            )
                        ]
                    }
                ]
            },
        )

    def test_create_product_without_eigenaren(self):
        response = self.client.post(self.path, self.data | {"eigenaren": []})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenaren": [
                    ErrorDetail(
                        string=_("Er is minimaal één eigenaar vereist."),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_vestigingsnummer_and_kvk(self):
        data = self.data | {
            "eigenaren": [{"vestingsnummer": "123", "kvk_nummer": "12345678"}]
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 1)

    def test_update_product(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=["verlopen"])
        product = ProductFactory.create(producttype=producttype)

        data = self.data | {
            "eind_datum": datetime.date(2025, 12, 31),
            "producttype_id": producttype.id,
            "eigenaren": [{"kvk_nummer": "12345678"}],
        }
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().eind_datum, data["eind_datum"])

    def test_update_product_with_not_allowed_state(self):
        product = ProductFactory.create()
        data = self.data.copy() | {"status": "actief"}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    ErrorDetail(
                        string=_(
                            "Status 'Actief' is niet toegestaan voor het producttype {}."
                        ).format(self.producttype.naam),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_removing_eigenaren(self):
        product = ProductFactory.create()
        EigenaarFactory.create(product=product, bsn="111222333")
        EigenaarFactory.create(product=product, kvk_nummer="12345678")

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_("Er is minimaal één eigenaar vereist."),
                    code="invalid",
                )
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(
                self.detail_path(product), self.data | {"eigenaren": []}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Eigenaar.objects.count(), 2)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), {"eigenaren": []})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Eigenaar.objects.count(), 2)
            self.assertEqual(response.data, expected_error)

    def test_update_updating_and_removing_eigenaren(self):
        product = ProductFactory.create()
        eigenaar_to_be_updated = EigenaarFactory.create(
            product=product, bsn="111222333"
        )
        EigenaarFactory.create(product=product, kvk_nummer="12345678")

        self.maxDiff = None

        data = {
            "eigenaren": [
                {
                    "id": eigenaar_to_be_updated.id,
                    "klantnummer": "1234",
                    "bsn": "",
                }
            ]
        }

        expected_data = [
            {
                "id": str(eigenaar_to_be_updated.id),
                "klantnummer": "1234",
                "bsn": "",
                "kvk_nummer": "",
                "vestigingsnummer": "",
            }
        ]

        with self.subTest("PUT"):

            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(response.data["eigenaren"], expected_data)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(response.data["eigenaren"], expected_data)

    def test_update_creating_and_removing_eigenaren(self):
        product = ProductFactory.create()
        EigenaarFactory.create(product=product, kvk_nummer="12345678")

        data = {"eigenaren": [{"klantnummer": "1234"}]}

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(Eigenaar.objects.get().klantnummer, "1234")

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(Eigenaar.objects.get().klantnummer, "1234")

    def test_update_product_with_eigenaar_not_part_of_product(self):
        product = ProductFactory.create()
        eigenaar_of_other_product = EigenaarFactory.create(kvk_nummer="12345678")

        data = {
            "eigenaren": [{"id": eigenaar_of_other_product.id, "klantnummer": "1234"}]
        }

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_(
                        "Eigenaar id {} op index 0 is niet onderdeel van het Product object."
                    ).format(eigenaar_of_other_product.id),
                    code="invalid",
                )
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

    def test_update_product_with_eigenaar_id_not_existing(self):
        product = ProductFactory.create()

        eigenaar_id = uuid.uuid4()

        data = {"eigenaren": [{"id": eigenaar_id, "klantnummer": "1234"}]}

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_("Eigenaar id {} op index 0 bestaat niet.").format(
                        eigenaar_id
                    ),
                    code="invalid",
                )
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

    def test_update_product_with_duplicate_eigenaren_ids(self):
        product = ProductFactory.create()
        eigenaar_to_be_updated = EigenaarFactory.create(
            product=product, bsn="111222333"
        )

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_("Dubbel id: {} op index 1.").format(
                        eigenaar_to_be_updated.id
                    ),
                    code="invalid",
                )
            ]
        }

        data = {
            "eigenaren": [
                {"id": eigenaar_to_be_updated.id, "klantnummer": "1234"},
                {"id": eigenaar_to_be_updated.id, "klantnummer": "5678"},
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

    def test_partial_update_product(self):
        product = ProductFactory.create(
            producttype=ProductTypeFactory.create(toegestane_statussen=["verlopen"]),
        )

        data = {"eind_datum": datetime.date(2025, 12, 31)}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().eind_datum, data["eind_datum"])

    def test_read_producten(self):
        product1 = ProductFactory.create(producttype=self.producttype)
        EigenaarFactory(kvk_nummer="12345678", product=product1)
        product2 = ProductFactory.create(producttype=self.producttype)
        EigenaarFactory(kvk_nummer="12345678", product=product2)

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "url": f"http://testserver{self.detail_path(product1)}",
                "id": str(product1.id),
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
                "eigenaren": [
                    {
                        "bsn": "",
                        "kvk_nummer": "12345678",
                        "vestigingsnummer": "",
                        "klantnummer": "",
                        "id": str(product1.eigenaren.get().id),
                    }
                ],
                "producttype": {
                    "id": str(self.producttype.id),
                    "code": self.producttype.code,
                    "uniforme_product_naam": self.producttype.uniforme_product_naam.naam,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": self.producttype.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.producttype.update_datum.astimezone().isoformat(),
                    "keywords": [],
                },
            },
            {
                "url": f"http://testserver{self.detail_path(product2)}",
                "id": str(product2.id),
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
                "eigenaren": [
                    {
                        "bsn": "",
                        "kvk_nummer": "12345678",
                        "vestigingsnummer": "",
                        "klantnummer": "",
                        "id": str(product2.eigenaren.get().id),
                    }
                ],
                "producttype": {
                    "id": str(self.producttype.id),
                    "code": self.producttype.code,
                    "uniforme_product_naam": self.producttype.uniforme_product_naam.naam,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": self.producttype.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.producttype.update_datum.astimezone().isoformat(),
                    "keywords": [],
                },
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    @freeze_time("2025-12-31")
    def test_read_product(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=["gereed"])
        product = ProductFactory.create(producttype=producttype)
        EigenaarFactory(kvk_nummer="12345678", product=product)

        response = self.client.get(self.detail_path(product))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "url": f"http://testserver{self.detail_path(product)}",
            "id": str(product.id),
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
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "id": str(product.eigenaren.get().id),
                }
            ],
            "producttype": {
                "id": str(producttype.id),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "toegestane_statussen": ["gereed"],
                "gepubliceerd": True,
                "aanmaak_datum": "2025-12-31T01:00:00+01:00",
                "update_datum": "2025-12-31T01:00:00+01:00",
                "keywords": [],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_product(self):
        product = ProductFactory.create()
        response = self.client.delete(self.detail_path(product))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_not_checked_when_not_changed(self):
        data = {
            "producttype_id": ProductTypeFactory.create(toegestane_statussen=[]).id,
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "frequentie": "eenmalig",
        }

        product = ProductFactory.create(**data)

        response = self.client.put(
            self.detail_path(product),
            data | {"eigenaren": [{"kvk_nummer": "12345678"}]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @freeze_time("2025-11-30")
    def test_partial_update_state_and_dates_are_not_checked_when_not_changed(self):
        data = {
            "producttype_id": ProductTypeFactory.create(toegestane_statussen=[]).id,
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)

        response = self.client.patch(self.detail_path(product), {"prijs": "50"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_checked_when_producttype_is_changed(self):
        new_producttype = ProductTypeFactory.create(toegestane_statussen=[])

        tests = [
            {
                "field": {"status": "gereed"},
                "error": {
                    "status": [
                        ErrorDetail(
                            string=_(
                                "Status 'Gereed' is niet toegestaan voor het producttype {}."
                            ).format(new_producttype.naam),
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
                                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het producttype."
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
                                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het producttype."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
        ]

        for test in tests:
            with self.subTest(
                f"Test {test['field']} is checked when producttype is changed."
            ):

                data = {
                    "producttype_id": ProductTypeFactory.create(
                        toegestane_statussen=[]
                    ).id,
                    "prijs": "10",
                    "frequentie": "eenmalig",
                } | test["field"]

                product = ProductFactory.create(**data)
                EigenaarFactory(product=product)

                response = self.client.put(
                    self.detail_path(product),
                    data
                    | {
                        "producttype_id": new_producttype.id,
                        "eigenaren": [{"kvk_nummer": "12345678"}],
                    },
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(response.data, test["error"])

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_checked_when_changed(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])
        tests = [
            {
                "field": {"status": "gereed"},
                "error": {
                    "status": [
                        ErrorDetail(
                            string=_(
                                "Status 'Gereed' is niet toegestaan voor het producttype {}."
                            ).format(producttype.naam),
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
                                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het producttype."
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
                                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het producttype."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
        ]

        for test in tests:
            with self.subTest(
                f"Test {test['field']} is checked when producttype is changed."
            ):

                data = {
                    "producttype_id": producttype.id,
                    "status": "initieel",
                    "prijs": "10",
                    "frequentie": "eenmalig",
                }

                product = ProductFactory.create(**data)

                response = self.client.put(
                    self.detail_path(product),
                    data | test["field"] | {"eigenaren": [{"kvk_nummer": "12345678"}]},
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(response.data, test["error"])
