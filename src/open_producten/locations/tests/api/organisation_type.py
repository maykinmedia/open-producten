from rest_framework.test import APIClient

from open_producten.locations.models import OrganisationType
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import OrganisationTypeFactory


def organisation_type_to_dict(organisation_type):
    return model_to_dict_with_id(organisation_type)


class TestOrganisationType(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.data = {"name": "type"}
        self.path = "/api/v1/organisationtypes/"

        self.organisation_type = OrganisationTypeFactory.create()

    def test_read_organisation_type_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_organisation_type(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(OrganisationType.objects.count(), 2)

    def test_update_organisation_type(self):
        data = self.data | {"name": "updated"}
        response = self.put(self.organisation_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(OrganisationType.objects.count(), 1)
        self.assertEqual(OrganisationType.objects.first().name, "updated")

    def test_partial_update_organisation_type(self):
        data = {"name": "updated"}
        response = self.patch(self.organisation_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(OrganisationType.objects.count(), 1)
        self.assertEqual(OrganisationType.objects.first().name, "updated")

    def test_read_organisation_types(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"],
            [organisation_type_to_dict(self.organisation_type)],
        )

    def test_read_organisation_type(self):
        response = self.get(self.organisation_type.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, organisation_type_to_dict(self.organisation_type)
        )

    def test_delete_organisation_type(self):
        response = self.delete(self.organisation_type.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(OrganisationType.objects.count(), 0)
