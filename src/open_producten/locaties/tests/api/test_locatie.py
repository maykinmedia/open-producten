from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point

from rest_framework.test import APIClient

from open_producten.locaties.models import Locatie
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import LocatieFactory


def locatie_to_dict(locatie):
    locatie_dict = model_to_dict_with_id(locatie, exclude="coordinaten")
    locatie_dict["coordinaten"] = locatie.coordinaten.coords

    return locatie_dict


@patch(
    "open_producten.locaties.models.locatie.geocode_address",
    new=Mock(return_value=Point((4.84303667, 52.38559043))),
)
class TestLocatie(BaseApiTestCase):

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def setUp(self):
        super().setUp()
        self.data = {"naam": "locatie", "postcode": "1111 AA", "stad": "Amsterdam"}
        self.path = "/api/v1/locaties/"

        self.locatie = LocatieFactory.create()

    def test_read_locatie_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_locatie(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Locatie.objects.count(), 2)

    def test_update_locatie(self):
        data = self.data | {"naam": "update"}
        response = self.put(self.locatie.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Locatie.objects.count(), 1)
        self.assertEqual(Locatie.objects.first().naam, "update")

    def test_partial_update_locatie(self):
        data = {"naam": "update"}
        response = self.patch(self.locatie.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Locatie.objects.count(), 1)
        self.assertEqual(Locatie.objects.first().naam, "update")

    def test_read_locaties(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [locatie_to_dict(self.locatie)])

    def test_read_locatie(self):
        response = self.get(self.locatie.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, locatie_to_dict(self.locatie))

    def test_delete_locatie(self):
        response = self.delete(self.locatie.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Locatie.objects.count(), 0)
