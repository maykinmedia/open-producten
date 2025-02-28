from uuid import uuid4

from django.urls import reverse

from freezegun import freeze_time
from rest_framework import status

from open_producten.producttypen.tests.factories import ThemaFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestThemaFilters(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.path = reverse("thema-list")

    def test_gepubliceerd_filter(self):
        ThemaFactory.create(gepubliceerd=True)
        ThemaFactory.create(gepubliceerd=False)

        response = self.client.get(self.path, {"gepubliceerd": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_naam_filter(self):
        ThemaFactory.create(naam="organisatie a")
        ThemaFactory.create(naam="organisatie b")

        response = self.client.get(self.path, {"naam": "organisatie b"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_hoofd_thema_naam_filter(self):
        hoofd_thema = ThemaFactory.create(naam="vervoer")
        ThemaFactory.create(hoofd_thema=hoofd_thema)
        ThemaFactory.create()

        response = self.client.get(self.path, {"hoofd_thema__naam": "vervoer"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_hoofd_thema_id_filter(self):
        hoofd_thema_id = uuid4()
        hoofd_thema = ThemaFactory.create(id=hoofd_thema_id)
        ThemaFactory.create(hoofd_thema=hoofd_thema)
        ThemaFactory.create()

        response = self.client.get(self.path + f"?hoofd_thema__id={hoofd_thema_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_aanmaak_datum_filter(self):
        with freeze_time("2024-06-07"):
            ThemaFactory.create()
        with freeze_time("2025-06-07"):
            ThemaFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"aanmaak_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(self.path, {"aanmaak_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(self.path, {"aanmaak_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_update_datum_filter(self):
        with freeze_time("2024-06-07"):
            ThemaFactory.create()
        with freeze_time("2025-06-07"):
            ThemaFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"update_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(self.path, {"update_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(self.path, {"update_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
