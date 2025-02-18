from django.urls import reverse

from rest_framework import status

from open_producten.producttypen.tests.factories import ProductTypeFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestLinkFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("producttype-list")

    def test_product_type_code_filter(self):
        ProductTypeFactory.create(code="123")
        ProductTypeFactory.create(code="8234098q2730492873")

        response = self.client.get(self.path + "?code=8234098q2730492873")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_upn_filter(self):
        ProductTypeFactory.create(uniforme_product_naam__naam="parkeervergunning")
        ProductTypeFactory.create(uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path + "?uniforme_product_naam=parkeervergunning"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
