from rest_framework.test import APIClient

from open_producten.locations.models import Location
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import LocationFactory


def location_to_dict(location):
    return model_to_dict_with_id(location)


class TestLocation(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.data = {"name": "locatie", "postcode": "1111 AA", "city": "Amsterdam"}
        self.path = "/api/v1/locations/"

    def _create_location(self):
        return LocationFactory.create()

    def test_read_location_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_location(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Location.objects.count(), 1)

    def test_update_location(self):
        location = self._create_location()

        data = self.data | {"name": "updated"}
        response = self.put(location.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Location.objects.count(), 1)

    def test_partial_update_location(self):
        location = self._create_location()

        data = {"name": "updated"}
        response = self.patch(location.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Location.objects.count(), 1)

    def test_read_locations(self):
        location = self._create_location()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [location_to_dict(location)])

    def test_read_location(self):
        location = self._create_location()

        response = self.get(location.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, location_to_dict(location))

    def test_delete_location(self):
        location = self._create_location()
        response = self.delete(location.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Location.objects.count(), 0)
