from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.urls import reverse

from rest_framework import status

from open_producten.producttypen.tests.factories import PrijsFactory, PrijsOptieFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestPrijsFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("prijs-list")

    def test_prijs_opties_bedrag_filter(self):
        prijs1 = PrijsFactory.create()
        PrijsOptieFactory.create(prijs=prijs1, bedrag=Decimal(10))
        PrijsOptieFactory.create(prijs=prijs1, bedrag=Decimal(30))
        prijs2 = PrijsFactory.create()
        PrijsOptieFactory.create(prijs=prijs2, bedrag=Decimal(50))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"prijsopties__bedrag": "50"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(self.path, {"prijsopties__bedrag__lte": "40"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(self.path, {"prijsopties__bedrag__gte": "40"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_prijs_opties_beschrijving_filter(self):
        prijs = PrijsFactory.create()
        PrijsFactory.create()

        PrijsOptieFactory.create(prijs=prijs, beschrijving="spoed")

        response = self.client.get(self.path, {"prijsopties__beschrijving": "spoed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_actief_vanaf_filter(self):
        PrijsFactory.create(actief_vanaf=date(2024, 6, 7))
        PrijsFactory.create(actief_vanaf=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"actief_vanaf": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(self.path, {"actief_vanaf__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(self.path, {"actief_vanaf__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_product_type_code_filter(self):
        PrijsFactory.create(product_type__code="123")
        PrijsFactory.create(product_type__code="8234098q2730492873")

        response = self.client.get(
            self.path, {"product_type__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_id_filter(self):
        product_type_id = uuid4()
        PrijsFactory.create(product_type__id=product_type_id)
        PrijsFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_upn_filter(self):
        PrijsFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning"
        )
        PrijsFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_naam_filter(self):
        PrijsFactory.create(product_type__naam="parkeervergunning")
        PrijsFactory.create(product_type__naam="aanbouw")

        response = self.client.get(
            self.path, {"product_type__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
