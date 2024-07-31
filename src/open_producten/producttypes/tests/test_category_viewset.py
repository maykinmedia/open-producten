from rest_framework.test import APITestCase

from .factories import CategoryFactory, ProductTypeFactory
from ..models import Category


class TestCategoryViewSet(APITestCase):

    def setUp(self):
        self.data = {
            "name": "test-category",
            "parent_category": None,
        }

    def test_create_minimal_category(self):
        response = self.client.post("/api/v1/categories/", self.data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_category_with_parent(self):
        parent = CategoryFactory.create()
        data = self.data | {"parent_category": parent.id}

        response = self.client.post("/api/v1/categories/", data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(id=response.data["id"]).get_parent(), parent)

    def test_create_category_with_product_type(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id]}

        response = self.client.post("/api/v1/categories/", data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().product_types.first(), product_type)

    def test_change_parent(self):
        new_parent = CategoryFactory.create()
        category = CategoryFactory.create()

        data = self.data | {"parent_category": new_parent.id}
        response = self.client.put(
            f"/api/v1/categories/{category.id}/", data, format="json"
        )

        category.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(category.get_parent(), new_parent)

    def test_add_question_to_product_type(self):
        category = CategoryFactory.create()

        data = {"question": "18?", "answer": "eligible"}
        response = self.client.post(
            f"/api/v1/categories/{category.id}/questions/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(category.questions.first().question, "18?")
