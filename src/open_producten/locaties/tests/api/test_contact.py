from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point

from rest_framework.test import APIClient

from open_producten.locaties.models import Contact
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import ContactFactory, OrganisatieFactory


def contact_to_dict(contact):
    contact_dict = model_to_dict_with_id(contact)
    contact_dict["organisatie"] = model_to_dict_with_id(
        contact.organisatie, exclude="coordinaten"
    )
    contact_dict["organisatie"]["coordinaten"] = contact.organisatie.coordinaten.coords

    return contact_dict


class TestContact(BaseApiTestCase):

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def setUp(self):
        super().setUp()
        organisatie = OrganisatieFactory.create()
        self.data = {
            "voornaam": "bob",
            "achternaam": "de vries",
            "organisatie_id": organisatie.id,
        }
        self.path = "/api/v1/contacten/"

        self.contact = ContactFactory.create()

    def test_read_contact_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_contact(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contact.objects.count(), 2)

    def test_update_contact(self):
        data = self.data | {"voornaam": "update"}
        response = self.put(self.contact.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.first().voornaam, "update")

    def test_partial_update_contact(self):
        data = {"voornaam": "update"}
        response = self.patch(self.contact.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.first().voornaam, "update")

    def test_read_contacts(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [contact_to_dict(self.contact)])

    def test_read_contact(self):
        response = self.get(self.contact.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, contact_to_dict(self.contact))

    def test_delete_contact(self):
        response = self.delete(self.contact.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Contact.objects.count(), 0)
