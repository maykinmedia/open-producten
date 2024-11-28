from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point

from rest_framework.test import APIClient

from open_producten.locaties.models import Organisatie
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import OrganisatieFactory


def organisatie_to_dict(organisatie):
    organisatie_dict = model_to_dict_with_id(organisatie, exclude="coordinaten")
    organisatie_dict["coordinaten"] = organisatie.coordinaten.coords

    return organisatie_dict


@patch(
    "open_producten.locaties.models.locatie.geocode_address",
    new=Mock(return_value=Point((4.84303667, 52.38559043))),
)
class TestOrganisatie(BaseApiTestCase):

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def setUp(self):
        super().setUp()

        self.data = {
            "naam": "locatie",
            "postcode": "1111 AA",
            "stad": "Amsterdam",
        }
        self.path = "/api/v1/organisaties/"

        self.organisatie = OrganisatieFactory.create()

    def test_read_organisatie_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_organisatie(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Organisatie.objects.count(), 2)

    def test_update_organisatie(self):
        data = self.data | {"naam": "update"}
        response = self.put(self.organisatie.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Organisatie.objects.count(), 1)
        self.assertEqual(Organisatie.objects.first().naam, "update")

    def test_partial_update_organisatie(self):
        data = {"naam": "update"}
        response = self.patch(self.organisatie.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Organisatie.objects.count(), 1)
        self.assertEqual(Organisatie.objects.first().naam, "update")

    def test_read_organisaties(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"], [organisatie_to_dict(self.organisatie)]
        )

    def test_read_organisatie(self):
        response = self.get(self.organisatie.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, organisatie_to_dict(self.organisatie))

    def test_delete_organisatie(self):
        response = self.delete(self.organisatie.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Organisatie.objects.count(), 0)
