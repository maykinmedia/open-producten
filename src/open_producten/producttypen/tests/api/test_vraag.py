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
from open_producten.utils.tests.helpers import model_to_dict_with_id


def vraag_to_dict(vraag):
    vraag_dict = model_to_dict_with_id(vraag, exclude=["product_type", "onderwerp"])
    vraag_dict["product_type_id"] = (
        vraag.product_type.id if vraag.product_type else None
    )
    vraag_dict["onderwerp_id"] = vraag.onderwerp.id if vraag.onderwerp else None

    return vraag_dict


class TestProductTypeVraag(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.onderwerp = OnderwerpFactory.create()
        self.data = {"vraag": "18?", "antwoord": "in aanmerking"}
        self.path = reverse("vraag-list")

        self.vraag = VraagFactory.create(product_type=self.product_type)

    def test_read_vraag_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_vraag(self):
        response = self.post(self.data | {"product_type_id": self.product_type.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vraag.objects.count(), 2)

    def test_create_vraag_with_onderwerp(self):
        response = self.post(self.data | {"onderwerp_id": self.onderwerp.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vraag.objects.count(), 2)

    def test_create_vraag_with_both_product_type_and_onderwerp(self):
        response = self.post(
            self.data
            | {
                "onderwerp_id": self.onderwerp.id,
                "product_type_id": self.product_type.id,
            }
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
        response = self.post(self.data)

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
        response = self.put(self.vraag.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().vragen.first().vraag, "21?")

    def test_update_vraag_with_onderwerp_and_product_type(self):
        data = self.data | {
            "vraag": "21?",
            "onderwerp_id": self.onderwerp.id,
            "product_type_id": self.product_type.id,
        }
        response = self.put(self.vraag.id, data)

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

    def test_partial_update_vraag(self):
        data = {"vraag": "21?"}
        response = self.patch(self.vraag.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().vragen.first().vraag, "21?")

    def test_partial_update_vraag_with_onderwerp(self):
        data = self.data | {"vraag": "21?", "onderwerp_id": self.onderwerp.id}
        response = self.patch(self.vraag.id, data)

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
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [vraag_to_dict(self.vraag)])

    def test_read_vraag(self):
        response = self.get(self.vraag.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, vraag_to_dict(self.vraag))

    def test_delete_vraag(self):
        response = self.delete(self.vraag.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Vraag.objects.count(), 0)
