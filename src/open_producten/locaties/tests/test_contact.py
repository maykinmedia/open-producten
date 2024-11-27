from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.test import TestCase

from .factories import ContactFactory, OrganisatieFactory


class ContactTestCase(TestCase):

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def setUp(self):
        organisatie = OrganisatieFactory.create(
            email="org@gmail.com", telefoonnummer="123456789", naam="Test Org"
        )
        self.contact = ContactFactory.create(
            organisatie=organisatie, voornaam="Bob", achternaam="de Vries"
        )

    def test_contact_str(self):
        self.assertEqual(str(self.contact), "Test Org: Bob de Vries")

        self.contact.organisatie = None
        self.contact.save()

        self.assertEqual(str(self.contact), "Bob de Vries")

    def test_get_email(self):
        self.assertEqual(self.contact.get_email(), "org@gmail.com")

        self.contact.email = "loc@gmail.com"
        self.contact.save()

        self.assertEqual(self.contact.get_email(), "loc@gmail.com")

    def test_get_phone_number(self):
        self.assertEqual(self.contact.get_phone_number(), "123456789")

        self.contact.telefoonnummer = "987654321"
        self.contact.save()

        self.assertEqual(self.contact.get_phone_number(), "987654321")
