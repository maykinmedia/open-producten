from rest_framework.test import APIClient

from open_producten.locations.models import Organisation
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import (
    NeighbourhoodFactory,
    OrganisationFactory,
    OrganisationTypeFactory,
)


def organisation_to_dict(organisation):
    organisation_dict = model_to_dict_with_id(organisation)
    organisation_dict["type"] = model_to_dict_with_id(organisation.type)
    organisation_dict["neighbourhood"] = model_to_dict_with_id(
        organisation.neighbourhood
    )
    return organisation_dict


class TestOrganisation(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        organisation_type = OrganisationTypeFactory.create()
        neighbourhood = NeighbourhoodFactory.create()
        self.data = {
            "name": "locatie",
            "postcode": "1111 AA",
            "city": "Amsterdam",
            "type_id": organisation_type.id,
            "neighbourhood_id": neighbourhood.id,
        }
        self.path = "/api/v1/organisations/"

    def _create_organisation(self):
        return OrganisationFactory.create()

    def test_read_organisation_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_organisation(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Organisation.objects.count(), 1)

    def test_update_organisation(self):
        organisation = self._create_organisation()

        data = self.data | {"name": "updated"}
        response = self.put(organisation.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Organisation.objects.count(), 1)

    def test_partial_update_organisation(self):
        organisation = self._create_organisation()

        data = {"name": "updated"}
        response = self.patch(organisation.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Organisation.objects.count(), 1)

    def test_read_organisations(self):
        organisation = self._create_organisation()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [organisation_to_dict(organisation)])

    def test_read_organisation(self):
        organisation = self._create_organisation()

        response = self.get(organisation.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, organisation_to_dict(organisation))

    def test_delete_organisation(self):
        organisation = self._create_organisation()
        response = self.delete(organisation.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Organisation.objects.count(), 0)
