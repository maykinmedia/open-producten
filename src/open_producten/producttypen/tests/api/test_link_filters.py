from uuid import uuid4

from django.urls import reverse_lazy

from rest_framework import status

from open_producten.producttypen.tests.factories import LinkFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestLinkFilters(BaseApiTestCase):

    path = reverse_lazy("link-list")

    def test_naam_filter(self):
        LinkFactory.create(naam="organisatie a")
        LinkFactory.create(naam="organisatie b")

        response = self.client.get(self.path, {"naam": "organisatie b"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["naam"], "organisatie b")

    def test_naam_contains_filter(self):
        LinkFactory.create(naam="organisatie a")
        LinkFactory.create(naam="organisatie b")

        response = self.client.get(self.path, {"naam__contains": "atie b"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["naam"], "organisatie b")

    def test_url_filter(self):
        LinkFactory.create(url="https://google.com")
        LinkFactory.create(url="https://maykinmedia.nl")

        response = self.client.get(self.path, {"url": "https://maykinmedia.nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["url"], "https://maykinmedia.nl")

    def test_url_contains_filter(self):
        LinkFactory.create(url="https://google.com")
        LinkFactory.create(url="https://maykinmedia.nl")

        response = self.client.get(self.path, {"url__contains": "maykin"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["url"], "https://maykinmedia.nl")

    def test_producttype_code_filter(self):
        producttype_id = uuid4()
        LinkFactory.create(producttype__code="123")
        LinkFactory.create(
            producttype__code="8234098q2730492873", producttype__id=producttype_id
        )

        response = self.client.get(
            self.path, {"producttype__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)

    def test_producttype_id_filter(self):
        producttype_id = uuid4()
        LinkFactory.create(producttype__id=producttype_id)
        LinkFactory.create(producttype__id=uuid4())

        response = self.client.get(self.path + f"?producttype__id={producttype_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)

    def test_producttype_upn_filter(self):
        producttype_id = uuid4()
        LinkFactory.create(
            producttype__uniforme_product_naam__naam="parkeervergunning",
            producttype__id=producttype_id,
        )
        LinkFactory.create(producttype__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)

    def test_producttype_naam_filter(self):
        producttype_id = uuid4()
        LinkFactory.create(
            producttype__naam="parkeervergunning", producttype__id=producttype_id
        )
        LinkFactory.create(producttype__naam="aanbouw")

        response = self.client.get(
            self.path, {"producttype__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)
