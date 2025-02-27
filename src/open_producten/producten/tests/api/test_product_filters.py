from datetime import date
from uuid import uuid4

from django.urls import reverse

from rest_framework import status

from open_producten.producten.models.product import PrijsFrequentieChoices
from open_producten.producten.tests.factories import ProductFactory
from open_producten.producttypen.models.producttype import ProductStateChoices
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProductFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("product-list")

    def test_gepubliceerd_filter(self):
        ProductFactory.create(gepubliceerd=True)
        ProductFactory.create(gepubliceerd=False)

        response = self.client.get(self.path, {"gepubliceerd": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_status_filter(self):
        ProductFactory.create(status=ProductStateChoices.INITIEEL)
        ProductFactory.create(status=ProductStateChoices.GEREED)

        response = self.client.get(self.path, {"status": "initieel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_frequentie_filter(self):
        ProductFactory.create(frequentie=PrijsFrequentieChoices.EENMALIG)
        ProductFactory.create(frequentie=PrijsFrequentieChoices.MAANDELIJKS)

        response = self.client.get(self.path, {"frequentie": "eenmalig"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_code_filter(self):
        ProductFactory.create(product_type__code="123")
        ProductFactory.create(product_type__code="8234098q2730492873")

        response = self.client.get(
            self.path, {"product_type__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_upn_filter(self):
        ProductFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning"
        )
        ProductFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_id_filter(self):
        product_type_id = uuid4()
        ProductFactory.create(product_type__id=product_type_id)
        ProductFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_start_datum_filter(self):
        ProductFactory.create(start_datum=date(2024, 6, 7))
        ProductFactory.create(start_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"start_datum": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(self.path, {"start_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(self.path, {"start_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_eind_datum_filter(self):
        ProductFactory.create(eind_datum=date(2024, 6, 7))
        ProductFactory.create(eind_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"eind_datum": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(self.path, {"eind_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(self.path, {"eind_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
