from django.urls import reverse

from rest_framework import status

from open_producten.locaties.tests.factories import OrganisatieFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestOrganisatieFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("organisatie-list")

    def test_naam_filter(self):
        OrganisatieFactory.create(naam="Maykin Media")
        OrganisatieFactory.create(naam="Gemeente A")

        response = self.client.get(self.path, {"naam__iexact": "Maykin Media"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_email_filter(self):
        OrganisatieFactory.create(email="bob@maykinmedia.nl")
        OrganisatieFactory.create(email="alice@maykinmedia.nl")

        response = self.client.get(self.path, {"email__iexact": "Bob@MaykinMedia.nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_telefoonnummer_filter(self):
        OrganisatieFactory.create(telefoonnummer="0611223344")
        OrganisatieFactory.create(telefoonnummer="0611223355")

        response = self.client.get(self.path, {"telefoonnummer__contains": "344"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_straat_filter(self):
        OrganisatieFactory.create(straat="Kingsfortweg")
        OrganisatieFactory.create(naam="Queensfortweg")

        response = self.client.get(self.path, {"straat__iexact": "kingsfortweg"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_huisnummer_filter(self):
        OrganisatieFactory.create(huisnummer="132AA")
        OrganisatieFactory.create(huisnummer="52")

        response = self.client.get(self.path, {"huisnummer__iexact": "132aa"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_postcode_filter(self):
        OrganisatieFactory.create(postcode="1111AA")
        OrganisatieFactory.create(postcode="2222BB")

        response = self.client.get(self.path, {"postcode": "1111AA"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_stad_filter(self):
        OrganisatieFactory.create(stad="Amsterdam")
        OrganisatieFactory.create(stad="Zaandam")

        response = self.client.get(self.path, {"stad": "Amsterdam"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_code_filter(self):
        OrganisatieFactory.create(code="123")
        OrganisatieFactory.create(code="8q30298472019387409")

        response = self.client.get(self.path, {"code": "8q30298472019387409"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
