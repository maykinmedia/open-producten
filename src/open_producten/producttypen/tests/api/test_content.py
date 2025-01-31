from django.urls import reverse
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import ContentElement, ContentLabel
from open_producten.utils.tests.cases import BaseApiTestCase

from ..factories import ContentElementFactory, ProductTypeFactory


class TestContentElement(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.label = ContentLabel.objects.create(naam="voorwaarden")

        self.data = {
            "labels": [self.label.naam],
            "content": "Voorwaarden",
            "product_type_id": self.product_type.id,
        }
        self.content_element = ContentElementFactory(
            content="Test Content", product_type=self.product_type
        )

        self.content_element.labels.add(self.label)
        self.content_element.save()

        self.path = reverse("content-list")
        self.detail_path = reverse("content-detail", args=[self.content_element.id])

    def test_read_content_element_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "content": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "product_type_id": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
            },
        )

    def test_create_content_element(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContentElement.objects.count(), 2)

        response.data.pop("id")
        expected_data = {
            "labels": [self.label.naam],
            "content": "Voorwaarden",
            "product_type_id": self.product_type.id,
            "taal": "nl",
        }
        self.assertEqual(response.data, expected_data)

    def test_update_content_element(self):
        data = self.data | {"content": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ContentElement.objects.count(), 1)
        self.assertEqual(ContentElement.objects.first().content, "update")

    def test_partial_update_content_element(self):
        data = {"content": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ContentElement.objects.count(), 1)
        self.assertEqual(ContentElement.objects.first().content, "update")

    def test_read_content_element(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "id": str(self.content_element.id),
            "content": self.content_element.content,
            "labels": [
                self.label.naam,
            ],
            "product_type_id": self.product_type.id,
            "taal": "nl",
        }
        self.assertEqual(response.data, expected_data)

    def test_read_content_element_in_other_language(self):
        content_element = ContentElementFactory.create()
        content_element.set_current_language("en")
        content_element.content = "content element EN"
        content_element.save()

        path = reverse("content-detail", args=[content_element.id])

        response = self.client.get(path, headers={"Accept-Language": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "content element EN")
        self.assertEqual(response.data["taal"], "en")

    def test_read_content_element_in_fallback_language(self):
        content_element = ContentElementFactory.create(content="content element NL")
        path = reverse("content-detail", args=[content_element.id])

        response = self.client.get(path, headers={"Accept-Language": "de"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "content element NL")
        self.assertEqual(response.data["taal"], "nl")

    def test_delete_content_element(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ContentElement.objects.count(), 0)


class TestContentElementActions(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.content_element = ContentElementFactory.create()

        self.path = reverse("content-vertaling", args=(self.content_element.id, "en"))

    def test_put_vertaling(self):

        data = {"content": "content EN"}
        response = self.client.put(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": str(self.content_element.id),
                "content": "content EN",
            },
        )
        self.content_element.set_current_language("en")
        self.assertEqual(self.content_element.content, "content EN")

        self.content_element.set_current_language("nl")
        self.assertNotEqual(self.content_element.content, "content EN")

    def test_delete_nonexistent_vertaling(self):
        path = reverse("content-vertaling", args=(self.content_element.id, "de"))

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_vertaling(self):
        self.content_element.set_current_language("en")
        self.content_element.content = "content EN"
        self.content_element.save()

        response = self.client.delete(self.path)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.content_element.refresh_from_db()
        self.assertFalse(self.content_element.has_translation("en"))
