import datetime
import uuid
from decimal import Decimal

from django.urls import reverse

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import Prijs, PrijsOptie, ProductType
from open_producten.producttypen.tests.factories import (
    PrijsFactory,
    PrijsOptieFactory,
    ProductTypeFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


@freeze_time("2024-01-01")
class TestProductTypePrijs(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory()
        self.prijs_data = {
            "actief_vanaf": datetime.date(2024, 1, 2),
            "product_type_id": self.product_type.id,
        }
        self.prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 1, 2)
        )

        self.path = reverse("prijs-list")
        self.detail_path = reverse("prijs-detail", args=[self.prijs.id])

    def test_read_prijs_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "actief_vanaf": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
                "prijsopties": [ErrorDetail("Dit veld is vereist.", code="required")],
                "product_type_id": [
                    ErrorDetail("Dit veld is vereist.", code="required")
                ],
            },
        )

    def test_create_prijs_with_empty_opties(self):
        response = self.client.post(self.path, self.prijs_data | {"prijsopties": []})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string="Er is minimaal één optie vereist.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_prijs_without_opties(self):
        response = self.client.post(self.path, self.prijs_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string="Dit veld is vereist.",
                        code="required",
                    )
                ]
            },
        )

    def test_create_prijs_with_prijs_opties(self):
        data = {
            "actief_vanaf": datetime.date(2024, 1, 3),
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
            "product_type_id": self.product_type.id,
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prijs.objects.count(), 2)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(
            PrijsOptie.objects.first().bedrag,
            Decimal("74.99"),
        )

    def test_update_prijs_removing_all_opties(self):
        PrijsOptieFactory.create(prijs=self.prijs)
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string="Er is minimaal één optie vereist.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_updating_and_removing_opties(self):

        optie_to_be_updated = PrijsOptieFactory.create(prijs=self.prijs)
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {
                    "id": optie_to_be_updated.id,
                    "bedrag": "20",
                    "beschrijving": optie_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().bedrag, Decimal("20"))

    def test_update_prijs_creating_and_deleting_opties(self):

        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsopties": [{"bedrag": "20", "beschrijving": "test"}],
            "product_type_id": self.product_type.id,
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().bedrag, Decimal("20"))

    def test_update_prijs_with_optie_not_part_of_prijs_returns_error(self):

        optie = PrijsOptieFactory.create(prijs=PrijsFactory.create())

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving}
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=f"Prijs optie id {optie.id} op index 0 is niet onderdeel van het prijs object.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_optie_with_unknown_id_returns_error(self):

        non_existing_id = uuid.uuid4()

        data = {
            "product_type_id": self.product_type.id,
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsopties": [
                {"id": non_existing_id, "bedrag": "20", "beschrijving": "test"}
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=f"Prijs optie id {non_existing_id} op index 0 bestaat niet.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_duplicate_optie_ids_returns_error(self):

        optie = PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {"id": optie.id, "bedrag": "40", "beschrijving": optie.beschrijving},
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=f"Dubbel id: {optie.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_prijs(self):

        PrijsOptieFactory.create(prijs=self.prijs)

        data = {"actief_vanaf": datetime.date(2024, 1, 4)}

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().prijzen.first().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsOptie.objects.count(), 1)

    def test_partial_update_prijs_updating_and_removing_opties(self):

        optie_to_be_updated = PrijsOptieFactory.create(prijs=self.prijs)
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsopties": [
                {
                    "id": optie_to_be_updated.id,
                    "bedrag": "20",
                    "beschrijving": optie_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().bedrag, Decimal("20"))

    def test_partial_update_prijs_creating_and_deleting_opties(self):

        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": datetime.date(2024, 1, 4),
            "prijsopties": [{"bedrag": "20", "beschrijving": "test"}],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().prijzen.first().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().beschrijving, "test")

    def test_partial_update_with_multiple_errors(self):

        optie = PrijsOptieFactory.create(prijs=self.prijs)
        optie_of_other_prijs = PrijsOptieFactory.create(prijs=PrijsFactory.create())
        non_existing_optie = uuid.uuid4()

        data = {
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {
                    "id": optie_of_other_prijs.id,
                    "bedrag": "30",
                    "beschrijving": optie_of_other_prijs.beschrijving,
                },
                {"id": non_existing_optie, "bedrag": "30", "beschrijving": "test"},
            ]
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=f"Dubbel id: {optie.id} op index 1.",
                        code="invalid",
                    ),
                    ErrorDetail(
                        string=f"Prijs optie id {optie_of_other_prijs.id} op index 2 is niet onderdeel van het prijs object.",
                        code="invalid",
                    ),
                    ErrorDetail(
                        string=f"Prijs optie id {non_existing_optie} op index 3 bestaat niet.",
                        code="invalid",
                    ),
                ]
            },
        )

    def test_read_prijzen(self):
        prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 2, 2)
        )
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.prijs.id),
                "actief_vanaf": str(self.prijs.actief_vanaf),
                "prijsopties": [],
                "product_type_id": self.product_type.id,
            },
            {
                "id": str(prijs.id),
                "actief_vanaf": str(prijs.actief_vanaf),
                "prijsopties": [],
                "product_type_id": self.product_type.id,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_prijs(self):
        response = self.client.get(self.detail_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(self.prijs.id),
            "actief_vanaf": str(self.prijs.actief_vanaf),
            "prijsopties": [],
            "product_type_id": self.product_type.id,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_prijs(self):

        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Prijs.objects.count(), 0)
        self.assertEqual(PrijsOptie.objects.count(), 0)
