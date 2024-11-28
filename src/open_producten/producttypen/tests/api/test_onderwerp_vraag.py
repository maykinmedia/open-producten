from django.forms import model_to_dict

from rest_framework.test import APIClient

from open_producten.producttypen.models import Onderwerp, Vraag
from open_producten.producttypen.tests.factories import OnderwerpFactory, VraagFactory
from open_producten.utils.tests.cases import BaseApiTestCase


def vraag_to_dict(vraag):
    return model_to_dict(vraag, exclude=["product_type", "onderwerp"]) | {
        "id": str(vraag.id)
    }


class TestOnderwerpVraag(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        onderwerp = OnderwerpFactory.create()
        self.data = {"vraag": "18?", "antwoord": "in aanmerking"}
        self.path = f"/api/v1/onderwerpen/{onderwerp.id}/vragen/"

        self.vraag = VraagFactory.create(onderwerp=onderwerp)

    def test_read_vraag_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_vraag(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vraag.objects.count(), 2)

    def test_update_vraag(self):
        data = self.data | {"vraag": "21?"}
        response = self.put(self.vraag.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(Onderwerp.objects.first().vragen.first().vraag, "21?")

    def test_partial_update_vraag(self):
        data = {"vraag": "21?"}
        response = self.patch(self.vraag.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vraag.objects.count(), 1)
        self.assertEqual(Onderwerp.objects.first().vragen.first().vraag, "21?")

    def test_read_vraags(self):
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
