from django.test import TestCase

from .factories import ContactFactory, OrganisationFactory


class ContactTestCase(TestCase):

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

    def test_get_mailto_link(self):
        self.assertEqual(self.contact.get_mailto_link(), "mailto://org@gmail.com")

        self.contact.email = "loc@gmail.com"
        self.contact.save()

        self.assertEqual(self.contact.get_mailto_link(), "mailto://loc@gmail.com")

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
