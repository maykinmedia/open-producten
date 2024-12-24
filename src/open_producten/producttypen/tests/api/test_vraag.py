from django.urls import reverse

from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import ProductType, Vraag
from open_producten.producttypen.tests.factories import (
    OnderwerpFactory,
    ProductTypeFactory,
    VraagFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProductTypeVraag(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.onderwerp = OnderwerpFactory.create()
        self.data = {"vraag": "18?", "antwoord": "in aanmerking"}
        self.vraag = VraagFactory.create(product_type=self.product_type)
        self.path = reverse("vraag-list")
        self.detail_path = reverse("vraag-detail", args=[self.vraag.id])

    def test_read_vraag_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "vraag": [ErrorDetail(string="Dit veld is vereist.", code="required")],
                "antwoord": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
            },
        )

    def test_create_vraag_with_product_type(self):
        response = self.client.post(
            self.path, self.data | {"product_type_id": self.product_type.id}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vraag.objects.count(), 2)
        response.data.pop("id")
        self.assertEqual(
            response.data,
            self.data | {"product_type_id": self.product_type.id, "onderwerp_id": None},
        )

    def test_create_vraag_with_onderwerp(self):
        response = self.client.post(
            self.path, self.data | {"onderwerp_id": self.onderwerp.id}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vraag.objects.count(), 2)
        response.data.pop("id")
        self.assertEqual(
            response.data,
            self.data | {"onderwerp_id": self.onderwerp.id, "product_type_id": None},
        )

    def test_create_vraag_with_both_product_type_and_onderwerp(self):
        response = self.client.post(
            self.path,
            self.data
            | {
                "onderwerp_id": self.onderwerp.id,
                "product_type_id": self.product_type.id,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_onderwerp": [
                    ErrorDetail(
                        string="Een vraag kan niet gelink zijn aan een onderwerp en een product type.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_vraag_without_product_type_or_onderwerp(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_onderwerp": [
                    ErrorDetail(
                        string="Een vraag moet gelinkt zijn aan een onderwerp of een product type.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_vraag(self):
        data = self.data | {"vraag": "21?", "product_type_id": self.product_type.id}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().vragen.first().vraag, "21?")

    def test_update_vraag_with_onderwerp(self):
        data = self.data | {"vraag": "21?", "onderwerp_id": self.onderwerp.id}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_onderwerp": [
                    ErrorDetail(
                        string="Een vraag kan niet gelink zijn aan een onderwerp en een product type.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_vraag_with_onderwerp_and_product_type(self):
        data = self.data | {
            "vraag": "21?",
            "onderwerp_id": self.onderwerp.id,
            "product_type_id": self.product_type.id,
        }
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_onderwerp": [
                    ErrorDetail(
                        string="Een vraag kan niet gelink zijn aan een onderwerp en een product type.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_vraag_change_to_onderwerp(self):
        data = self.data | {
            "onderwerp_id": self.onderwerp.id,
            "product_type_id": None,
        }
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(Vraag.objects.first().product_type, None)
        self.assertEqual(Vraag.objects.first().onderwerp, self.onderwerp)

    def test_partial_update_vraag(self):
        data = {"vraag": "21?"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().vragen.first().vraag, "21?")

    def test_partial_update_vraag_with_onderwerp(self):
        data = {"vraag": "21?", "onderwerp_id": self.onderwerp.id}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_onderwerp": [
                    ErrorDetail(
                        string="Een vraag kan niet gelink zijn aan een onderwerp en een product type.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_read_vragen(self):
        vraag = VraagFactory.create(product_type=self.product_type)
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.vraag.id),
                "vraag": self.vraag.vraag,
                "antwoord": self.vraag.antwoord,
                "product_type_id": self.product_type.id,
                "onderwerp_id": None,
            },
            {
                "id": str(vraag.id),
                "vraag": vraag.vraag,
                "antwoord": vraag.antwoord,
                "product_type_id": self.product_type.id,
                "onderwerp_id": None,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_vraag(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, 200)
        expected_data = {
            "id": str(self.vraag.id),
            "vraag": self.vraag.vraag,
            "antwoord": self.vraag.antwoord,
            "product_type_id": self.product_type.id,
            "onderwerp_id": None,
        }

        self.assertEqual(response.data, expected_data)

    def test_delete_vraag(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Vraag.objects.count(), 0)
