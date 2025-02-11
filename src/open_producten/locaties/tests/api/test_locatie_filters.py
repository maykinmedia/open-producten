from django.urls import reverse

from rest_framework import status

from open_producten.locaties.tests.factories import LocatieFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestLocatieFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("locatie-list")

    def test_naam_filter(self):
        LocatieFactory.create(naam="Maykin Media")
        LocatieFactory.create(naam="Gemeente A")

        response = self.client.get(self.path + "?naam__iexact=Maykin Media")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_email_filter(self):
        LocatieFactory.create(email="bob@maykinmedia.nl")
        LocatieFactory.create(email="alice@maykinmedia.nl")

        response = self.client.get(self.path + "?email__iexact=Bob@MaykinMedia.nl")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_telefoonnummer_filter(self):
        LocatieFactory.create(telefoonnummer="0611223344")
        LocatieFactory.create(telefoonnummer="0611223355")

        response = self.client.get(self.path + "?telefoonnummer__contains=344")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_straat_filter(self):
        LocatieFactory.create(straat="Kingsfortweg")
        LocatieFactory.create(naam="Queensfortweg")

        response = self.client.get(self.path + "?straat__iexact=kingsfortweg")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_huisnummer_filter(self):
        LocatieFactory.create(huisnummer="132AA")
        LocatieFactory.create(huisnummer="52")

        response = self.client.get(self.path + "?huisnummer__iexact=132aa")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_postcode_filter(self):
        LocatieFactory.create(postcode="1111AA")
        LocatieFactory.create(postcode="2222BB")

        response = self.client.get(self.path + "?postcode=1111AA")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_stad_filter(self):
        LocatieFactory.create(stad="Amsterdam")
        LocatieFactory.create(stad="Zaandam")

        response = self.client.get(self.path + "?stad=Amsterdam")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
