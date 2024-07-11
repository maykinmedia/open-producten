from django.test import TestCase

from ..admin.producttype import ProductTypeAdminForm
from ..models import Category
from .factories import CategoryFactory, UniformProductNameFactory


class TestProductTypeAdinForm(TestCase):
    def setUp(self):
        upn = UniformProductNameFactory.create()
        self.data = {
            "name": "test",
            "uniform_product_name": upn,
            "content": "content",
            "summary": "summary",
        }

    def test_at_least_one_category(self):
        form = ProductTypeAdminForm(data=self.data)

        self.assertEquals(
            form.errors, {"categories": ["At least one category is required"]}
        )

        CategoryFactory.create()
        form = ProductTypeAdminForm(
            data=self.data | {"categories": Category.objects.all()}
        )

        self.assertEquals(form.errors, {})
