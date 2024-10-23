from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point

from rest_framework.test import APIClient

from open_producten.locations.models import Location
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import LocationFactory


def location_to_dict(location):
    return model_to_dict_with_id(location)


@patch(
    "open_producten.locations.models.location.geocode_address",
    new=Mock(return_value=Point((4.84303667, 52.38559043))),
)
class TestLocation(BaseApiTestCase):

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def setUp(self):
        super().setUp()
        self.data = {"name": "locatie", "postcode": "1111 AA", "city": "Amsterdam"}
        self.path = "/api/v1/locations/"

        self.location = LocationFactory.create()

    def test_read_location_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_location(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 2)

    def test_update_location(self):
        data = self.data | {"name": "updated"}
        response = self.put(self.location.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.first().name, "updated")

    def test_partial_update_location(self):
        data = {"name": "updated"}
        response = self.patch(self.location.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.first().name, "updated")

    def test_read_locations(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [location_to_dict(self.location)])

    def test_read_location(self):
        response = self.get(self.location.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, location_to_dict(self.location))

    def test_delete_location(self):
        response = self.delete(self.location.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Location.objects.count(), 0)
