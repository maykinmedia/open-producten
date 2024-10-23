from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.test import TestCase

from .factories import ContactFactory, OrganisationFactory


class ContactTestCase(TestCase):

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def setUp(self):
        organisation = OrganisationFactory.create(
            email="org@gmail.com", phone_number="123456789", name="Test Org"
        )
        self.contact = ContactFactory.create(
            organisation=organisation, first_name="Bob", last_name="de Vries"
        )

    def test_contact_str(self):
        self.assertEqual(str(self.contact), "Test Org: Bob de Vries")

        self.contact.organisation = None
        self.contact.save()

        self.assertEqual(str(self.contact), "Bob de Vries")

    def test_get_email(self):
        self.assertEqual(self.contact.get_email(), "org@gmail.com")

        self.contact.email = "loc@gmail.com"
        self.contact.save()

        self.assertEqual(self.contact.get_email(), "loc@gmail.com")

    def test_get_phone_number(self):
        self.assertEqual(self.contact.get_phone_number(), "123456789")

        self.contact.phone_number = "987654321"
        self.contact.save()

        self.assertEqual(self.contact.get_phone_number(), "987654321")
