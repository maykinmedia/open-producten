from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point

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


@patch(
    "open_producten.locations.models.location.geocode_address",
    new=Mock(return_value=Point((4.84303667, 52.38559043))),
)
class TestOrganisation(BaseApiTestCase):

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
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

        self.organisation = OrganisationFactory.create()

    def test_read_organisation_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_organisation(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Organisation.objects.count(), 2)

    def test_update_organisation(self):
        data = self.data | {"name": "updated"}
        response = self.put(self.organisation.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertEqual(Organisation.objects.first().name, "updated")

    def test_partial_update_organisation(self):
        data = {"name": "updated"}
        response = self.patch(self.organisation.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertEqual(Organisation.objects.first().name, "updated")

    def test_read_organisations(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"], [organisation_to_dict(self.organisation)]
        )

    def test_read_organisation(self):
        response = self.get(self.organisation.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, organisation_to_dict(self.organisation))

    def test_delete_organisation(self):
        response = self.delete(self.organisation.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Organisation.objects.count(), 0)
