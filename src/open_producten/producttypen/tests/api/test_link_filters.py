from uuid import uuid4

from django.urls import reverse

from rest_framework import status

from open_producten.producttypen.tests.factories import LinkFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestLinkFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("link-list")

    def test_naam_filter(self):
        LinkFactory.create(naam="organisatie a")
        LinkFactory.create(naam="organisatie b")

        response = self.client.get(self.path + "?naam=organisatie b")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_naam_contains_filter(self):
        LinkFactory.create(naam="organisatie a")
        LinkFactory.create(naam="organisatie b")

        response = self.client.get(self.path + "?naam__contains=atie b")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_url_filter(self):
        LinkFactory.create(url="https://google.com")
        LinkFactory.create(url="https://maykinmedia.nl")

        response = self.client.get(self.path + "?url=https://maykinmedia.nl")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_url_contains_filter(self):
        LinkFactory.create(url="https://google.com")
        LinkFactory.create(url="https://maykinmedia.nl")

        response = self.client.get(self.path + "?url__contains=maykin")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_code_filter(self):
        LinkFactory.create(product_type__code="123")
        LinkFactory.create(product_type__code="8234098q2730492873")

        response = self.client.get(self.path + "?product_type__code=8234098q2730492873")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_id_filter(self):
        product_type_id = uuid4()
        LinkFactory.create(product_type__id=product_type_id)
        LinkFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_product_type_upn_filter(self):
        LinkFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning"
        )
        LinkFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path + "?uniforme_product_naam=parkeervergunning"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
