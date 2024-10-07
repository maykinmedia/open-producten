from rest_framework.test import APIClient

from open_producten.locations.models import Neighbourhood
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import NeighbourhoodFactory


def neighbourhood_to_dict(neighbourhood):
    return model_to_dict_with_id(neighbourhood)


class TestNeighbourhood(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.data = {"name": "buurt"}
        self.path = "/api/v1/neighbourhoods/"

    def _create_neighbourhood(self):
        return NeighbourhoodFactory.create()

    def test_read_neighbourhood_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_neighbourhood(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Neighbourhood.objects.count(), 1)

    def test_update_neighbourhood(self):
        neighbourhood = self._create_neighbourhood()

        data = self.data | {"name": "updated"}
        response = self.put(neighbourhood.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Neighbourhood.objects.count(), 1)

    def test_partial_update_neighbourhood(self):
        neighbourhood = self._create_neighbourhood()

        data = {"name": "updated"}
        response = self.patch(neighbourhood.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Neighbourhood.objects.count(), 1)

    def test_read_neighbourhoods(self):
        neighbourhood = self._create_neighbourhood()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"], [neighbourhood_to_dict(neighbourhood)]
        )

    def test_read_neighbourhood(self):
        neighbourhood = self._create_neighbourhood()

        response = self.get(neighbourhood.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, neighbourhood_to_dict(neighbourhood))

    def test_delete_neighbourhood(self):
        neighbourhood = self._create_neighbourhood()
        response = self.delete(neighbourhood.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Neighbourhood.objects.count(), 0)
