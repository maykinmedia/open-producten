import datetime
import uuid
from decimal import Decimal

from django.forms import model_to_dict
from django.urls import reverse

from freezegun import freeze_time
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import Prijs, PrijsOptie, ProductType
from open_producten.producttypen.tests.factories import (
    PrijsFactory,
    PrijsOptieFactory,
    ProductTypeFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id


def prijs_to_dict(prijs):
    prijs_dict = model_to_dict_with_id(prijs, exclude=["product_type"])
    prijs_dict["product_type_id"] = prijs.product_type.id
    prijs_dict["prijsopties"] = [
        model_to_dict(optie) for optie in prijs.prijsopties.all()
    ]
    prijs_dict["actief_vanaf"] = str(prijs_dict["actief_vanaf"])

    return prijs_dict


@freeze_time("2024-01-01")
class TestProductTypePrijs(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory()
        self.prijs_data = {
            "actief_vanaf": datetime.date(2024, 1, 2),
            "product_type_id": self.product_type.id,
        }
        self.path = reverse("prijs-list")

    def _create_prijs(self):
        return PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 1, 2)
        )

    def test_read_prijs_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_prijs_without_opties(self):
        response = self.post(self.prijs_data)

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

    def test_create_prijs_with_prijs_opties(self):
        data = {
            "actief_vanaf": datetime.date(2024, 1, 2),
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
            "product_type_id": self.product_type.id,
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(
            self.product_type.prijzen.first().prijsopties.first().bedrag,
            Decimal("74.99"),
        )

    def test_update_prijs_removing_all_opties(self):
        prijs = self._create_prijs()
        PrijsOptieFactory.create(prijs=prijs)
        PrijsOptieFactory.create(prijs=prijs)

        data = {
            "actief_vanaf": prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [],
        }

        response = self.put(prijs.id, data)

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

    def test_update_prijs_updating_and_removing_opties(self):
        prijs = self._create_prijs()
        optie_to_be_updated = PrijsOptieFactory.create(prijs=prijs)
        PrijsOptieFactory.create(prijs=prijs)

        data = {
            "actief_vanaf": prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {
                    "id": optie_to_be_updated.id,
                    "bedrag": "20",
                    "beschrijving": optie_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.put(prijs.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().bedrag, Decimal("20"))

    def test_update_prijs_creating_and_deleting_opties(self):
        prijs = self._create_prijs()
        PrijsOptieFactory.create(prijs=prijs)

        data = {
            "actief_vanaf": prijs.actief_vanaf,
            "prijsopties": [{"bedrag": "20", "beschrijving": "test"}],
            "product_type_id": self.product_type.id,
        }

        response = self.put(prijs.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().bedrag, Decimal("20"))

    def test_update_prijs_with_optie_not_part_of_prijs_returns_error(self):
        prijs = self._create_prijs()

        optie = PrijsOptieFactory.create(prijs=PrijsFactory.create())

        data = {
            "actief_vanaf": prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving}
            ],
        }

        response = self.put(prijs.id, data)

        self.assertEqual(response.status_code, 400)
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
        prijs = self._create_prijs()
        non_existing_id = uuid.uuid4()

        data = {
            "product_type_id": self.product_type.id,
            "actief_vanaf": prijs.actief_vanaf,
            "prijsopties": [
                {"id": non_existing_id, "bedrag": "20", "beschrijving": "test"}
            ],
        }

        response = self.put(prijs.id, data)

        self.assertEqual(response.status_code, 400)
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
        prijs = self._create_prijs()

        optie = PrijsOptieFactory.create(prijs=prijs)

        data = {
            "actief_vanaf": prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {"id": optie.id, "bedrag": "40", "beschrijving": optie.beschrijving},
            ],
        }

        response = self.put(prijs.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=f"Dubbele optie id {optie.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_prijs(self):
        prijs = self._create_prijs()
        PrijsOptieFactory.create(prijs=prijs)

        data = {"actief_vanaf": datetime.date(2024, 1, 4)}

        response = self.patch(prijs.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().prijzen.first().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsOptie.objects.count(), 1)

    def test_partial_update_prijs_updating_and_removing_opties(self):
        prijs = self._create_prijs()
        optie_to_be_updated = PrijsOptieFactory.create(prijs=prijs)
        PrijsOptieFactory.create(prijs=prijs)

        data = {
            "actief_vanaf": prijs.actief_vanaf,
            "prijsopties": [
                {
                    "id": optie_to_be_updated.id,
                    "bedrag": "20",
                    "beschrijving": optie_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.patch(prijs.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().bedrag, Decimal("20"))

    def test_partial_update_prijs_creating_and_deleting_opties(self):
        prijs = self._create_prijs()
        PrijsOptieFactory.create(prijs=prijs)

        data = {
            "actief_vanaf": datetime.date(2024, 1, 4),
            "prijsopties": [{"bedrag": "20", "beschrijving": "test"}],
        }

        response = self.patch(prijs.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().prijzen.first().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.first().beschrijving, "test")

    def test_partial_update_with_multiple_errors(self):
        prijs = self._create_prijs()
        optie = PrijsOptieFactory.create(prijs=prijs)
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

        response = self.patch(prijs.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=f"Dubbele optie id {optie.id} op index 1.",
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
        prijs = self._create_prijs()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [prijs_to_dict(prijs)])

    def test_read_prijs(self):
        prijs = self._create_prijs()

        response = self.get(prijs.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, prijs_to_dict(prijs))

    def test_delete_prijs(self):
        prijs = self._create_prijs()
        response = self.delete(prijs.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Prijs.objects.count(), 0)
        self.assertEqual(PrijsOptie.objects.count(), 0)
