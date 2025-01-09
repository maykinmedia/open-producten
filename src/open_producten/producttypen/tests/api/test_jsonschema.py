from django.urls import reverse

from django_json_schema.models import JsonSchema
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.utils.tests.cases import BaseApiTestCase


class TestProductTypeSchema(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.data = {
            "name": "parkeervergunning-verbruiksobject",
            "schema": {
                "type": "object",
                "properties": {"uren": {"type": "number"}},
                "required": ["uren"],
            },
        }
        self.schema = JsonSchema.objects.create(**self.data)

        self.path = reverse("schema-list")
        self.detail_path = reverse("schema-detail", args=[self.schema.id])

    def test_read_schema_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "name": [ErrorDetail(string="Dit veld is vereist.", code="required")],
                "schema": [ErrorDetail(string="Dit veld is vereist.", code="required")],
            },
        )

    def test_create_schema(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JsonSchema.objects.count(), 2)

        response.data.pop("id")
        self.assertEqual(response.data, self.data)

    def test_update_schema(self):
        data = self.data | {"name": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JsonSchema.objects.count(), 1)
        self.assertEqual(JsonSchema.objects.first().name, "update")

    def test_partial_update_schema(self):
        data = {"name": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JsonSchema.objects.count(), 1)
        self.assertEqual(JsonSchema.objects.first().name, "update")

    def test_read_schemas(self):
        schema = JsonSchema.objects.create(name="test", schema={})
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": self.schema.id,
                "name": self.schema.name,
                "schema": self.schema.schema,
            },
            {
                "id": schema.id,
                "name": schema.name,
                "schema": schema.schema,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_schema(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "id": self.schema.id,
            "name": self.schema.name,
            "schema": self.schema.schema,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_schema(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(JsonSchema.objects.count(), 0)
