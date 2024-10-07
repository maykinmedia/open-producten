from rest_framework.test import APIClient

from open_producten.locations.models import Contact
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import ContactFactory, OrganisationFactory


def contact_to_dict(contact):
    contact_dict = model_to_dict_with_id(contact)
    contact_dict["organisation"] = model_to_dict_with_id(contact.organisation)
    contact_dict["organisation"]["type"] = model_to_dict_with_id(
        contact.organisation.type
    )
    contact_dict["organisation"]["neighbourhood"] = model_to_dict_with_id(
        contact.organisation.neighbourhood
    )
    return contact_dict


class TestContact(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        organisation = OrganisationFactory.create()
        self.data = {
            "first_name": "bob",
            "last_name": "de vries",
            "organisation_id": organisation.id,
        }
        self.path = "/api/v1/contacts/"

    def _create_contact(self):
        return ContactFactory.create()

    def test_read_contact_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_contact(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contact.objects.count(), 1)

    def test_update_contact(self):
        contact = self._create_contact()

        data = self.data | {"name": "updated"}
        response = self.put(contact.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)

    def test_partial_update_contact(self):
        contact = self._create_contact()

        data = {"name": "updated"}
        response = self.patch(contact.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)

    def test_read_contacts(self):
        contact = self._create_contact()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [contact_to_dict(contact)])

    def test_read_contact(self):
        contact = self._create_contact()

        response = self.get(contact.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, contact_to_dict(contact))

    def test_delete_contact(self):
        contact = self._create_contact()
        response = self.delete(contact.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Contact.objects.count(), 0)
