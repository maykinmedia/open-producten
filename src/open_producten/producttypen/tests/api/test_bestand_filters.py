from uuid import uuid4

from django.core.files.base import ContentFile
from django.urls import reverse

from rest_framework import status

from open_producten.producttypen.tests.factories import BestandFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestBestandFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("bestand-list")

    def test_naam_filter(self):
        BestandFactory.create(bestand=ContentFile(b"abc", "abc.txt"))
        BestandFactory.create()

        response = self.client.get(self.path, {"naam__contains": "abc"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_code_filter(self):
        BestandFactory.create(product_type__code="123")
        BestandFactory.create(product_type__code="8234098q2730492873")

        response = self.client.get(
            self.path, {"product_type__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_id_filter(self):
        product_type_id = uuid4()
        BestandFactory.create(product_type__id=product_type_id)
        BestandFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_upn_filter(self):
        BestandFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning"
        )
        BestandFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_naam_filter(self):
        BestandFactory.create(product_type__naam="parkeervergunning")
        BestandFactory.create(product_type__naam="aanbouw")

        response = self.client.get(
            self.path, {"product_type__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
