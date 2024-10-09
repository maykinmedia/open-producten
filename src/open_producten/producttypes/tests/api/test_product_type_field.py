from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypes.models import Field, ProductType
from open_producten.producttypes.tests.factories import FieldFactory, ProductTypeFactory
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id


def field_to_dict(field):
    return model_to_dict_with_id(field, exclude=["product_type"])


class TestProductTypeField(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.data = {"name": "test field", "description": "test", "type": "textfield"}
        self.path = f"/api/v1/producttypes/{self.product_type.id}/fields/"

        self.field = FieldFactory.create(product_type=self.product_type)

    def test_read_field_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_field(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Field.objects.count(), 2)

    def test_create_normal_field_with_choices_returns_error(self):
        response = self.post(self.data | {"choices": ["a", "b"]})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "choices": [
                    ErrorDetail(string="textfield cannot have choices", code="invalid")
                ]
            },
        )

    def test_create_choice_field_without_choices_returns_error(self):
        response = self.post(self.data | {"type": "select"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "choices": [
                    ErrorDetail(
                        string="Choices are required for select", code="invalid"
                    )
                ]
            },
        )

    def test_update_field(self):
        data = self.data | {"name": "updated"}
        response = self.put(self.field.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().fields.first().name, "updated")

    def test_partial_update_field(self):
        data = {"name": "updated"}
        response = self.patch(self.field.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().fields.first().name, "updated")

    def test_partial_update_change_choices(self):
        field = FieldFactory.create(
            product_type=self.product_type, type="select", choices=["a", "b"]
        )

        data = {"choices": ["a"]}
        response = self.patch(field.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Field.objects.count(), 2)
        self.assertEqual(
            ProductType.objects.first().fields.get(id=field.id).choices, ["a"]
        )

    def test_read_fields(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [field_to_dict(self.field)])

    def test_read_field(self):
        response = self.get(self.field.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, field_to_dict(self.field))

    def test_delete_field(self):
        response = self.delete(self.field.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Field.objects.count(), 0)
