from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.locaties.models import Locatie
from open_producten.utils.tests.cases import BaseApiTestCase

from ..factories import LocatieFactory


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
        self.locatie = LocatieFactory.create()

        self.path = reverse("locatie-list")
        self.detail_path = reverse("locatie-detail", args=[self.locatie.id])

    def test_read_locatie_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "postcode": [
                    ErrorDetail(string="Dit veld is vereist.", code="required")
                ],
                "stad": [ErrorDetail(string="Dit veld is vereist.", code="required")],
            },
        )

    def test_create_locatie(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Locatie.objects.count(), 2)

        locatie = Locatie.objects.get(id=response.data["id"])
        expected_data = {
            "id": str(locatie.id),
            "naam": locatie.naam,
            "email": locatie.email,
            "telefoonnummer": locatie.telefoonnummer,
            "straat": locatie.straat,
            "huisnummer": locatie.huisnummer,
            "postcode": locatie.postcode,
            "stad": locatie.stad,
            "coordinaten": locatie.coordinaten.coords,
        }
        self.assertEqual(response.data, expected_data)

    def test_update_locatie(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Locatie.objects.count(), 1)
        self.assertEqual(Locatie.objects.first().naam, "update")

    def test_partial_update_locatie(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Locatie.objects.count(), 1)
        self.assertEqual(Locatie.objects.first().naam, "update")

    def test_read_locaties(self):
        locatie = LocatieFactory.create()
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.locatie.id),
                "naam": self.locatie.naam,
                "email": self.locatie.email,
                "telefoonnummer": self.locatie.telefoonnummer,
                "straat": self.locatie.straat,
                "huisnummer": self.locatie.huisnummer,
                "postcode": self.locatie.postcode,
                "stad": self.locatie.stad,
                "coordinaten": self.locatie.coordinaten.coords,
            },
            {
                "id": str(locatie.id),
                "naam": locatie.naam,
                "email": locatie.email,
                "telefoonnummer": locatie.telefoonnummer,
                "straat": locatie.straat,
                "huisnummer": locatie.huisnummer,
                "postcode": locatie.postcode,
                "stad": locatie.stad,
                "coordinaten": locatie.coordinaten.coords,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_locatie(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(self.locatie.id),
            "naam": self.locatie.naam,
            "email": self.locatie.email,
            "telefoonnummer": self.locatie.telefoonnummer,
            "straat": self.locatie.straat,
            "huisnummer": self.locatie.huisnummer,
            "postcode": self.locatie.postcode,
            "stad": self.locatie.stad,
            "coordinaten": self.locatie.coordinaten.coords,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_locatie(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Locatie.objects.count(), 0)
