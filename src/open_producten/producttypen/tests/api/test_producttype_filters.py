from django.urls import reverse

from rest_framework import status

from open_producten.producttypen.tests.factories import (
    ExterneCodeFactory,
    ProductTypeFactory,
    UniformeProductNaamFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestLinkFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("producttype-list")

    def test_gepubliceerd_filter(self):
        ProductTypeFactory.create(gepubliceerd=True)
        ProductTypeFactory.create(gepubliceerd=False)

        response = self.client.get(self.path, {"gepubliceerd": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_uniforme_product_naam_filter(self):
        ProductTypeFactory.create(
            uniforme_product_naam=UniformeProductNaamFactory(naam="parkeervergunning")
        )
        ProductTypeFactory.create(
            uniforme_product_naam=UniformeProductNaamFactory(naam="aanleunwoning")
        )

        response = self.client.get(
            self.path + "?uniforme_product_naam=parkeervergunning"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_externe_code_filter(self):
        product_type_1 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="12345", product_type=product_type_1)

        product_type_2 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="9837549857", product_type=product_type_2)

        response = self.client.get(self.path, {"externe_code": "[ISO:12345]"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_multiple_externe_code_filters(self):
        product_type_1 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="12345", product_type=product_type_1)
        ExterneCodeFactory(naam="OSI", code="456", product_type=product_type_1)

        product_type_2 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="9837549857", product_type=product_type_2)

        response = self.client.get(
            self.path, {"externe_code": ("[ISO:12345]", "[OSI:456]")}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_externe_code_filter_without_brackets(self):
        response = self.client.get(self.path, {"externe_code": "abc"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter_without_key_value(self):
        response = self.client.get(self.path, {"externe_code": "[:]"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter_with_invalid_characters(self):
        response = self.client.get(self.path, {"externe_code": "[a[b:[b:a]]"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_letter_filter(self):
        product_type_1 = ProductTypeFactory.create(naam="Parkeervergunning")
        product_type_2 = ProductTypeFactory.create(naam="Aanbouw")

        with self.subTest("NL"):
            response = self.client.get(
                self.path + "?letter=P", headers={"Accept-Language": "nl"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["naam"], "Parkeervergunning")

        with self.subTest("EN"):
            product_type_1.set_current_language("en")
            product_type_1.naam = "ssss"
            product_type_1.save()

            product_type_2.set_current_language("en")
            product_type_2.naam = "qqqq"
            product_type_2.save()

            response = self.client.get(
                self.path + "?letter=q", headers={"Accept-Language": "en"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["naam"], "qqqq")
