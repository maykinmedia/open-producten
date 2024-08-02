import datetime
from decimal import Decimal

from freezegun import freeze_time
from rest_framework.test import APITestCase

from ..models import Field, Link, Price, PriceOption, ProductType, Question
from .factories import (
    CategoryFactory,
    ConditionFactory,
    PriceFactory,
    PriceOptionFactory,
    ProductTypeFactory,
    TagFactory,
    UniformProductNameFactory,
)


class TestProducttypeViewSet(APITestCase):
    def setUp(self):
        upn = UniformProductNameFactory.create()

        self.data = {
            "name": "test-product-type",
            "summary": "test",
            "content": "test test",
            "uniform_product_name": upn.id,
        }

    def tearDown(self):
        ProductType.objects.all().delete()
        print(1)

    def test_create_minimal_product_type(self):
        response = self.client.post("/api/v1/producttypes/", self.data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_create_product_type_with_related_type(self):
        product_type = ProductTypeFactory.create()

        data = self.data | {"related_product_types": [product_type.id]}
        response = self.client.post("/api/v1/producttypes/", data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 2)
        self.assertEqual(
            ProductType.objects.get(id=response.data["id"])
            .related_product_types.first()
            .name,
            product_type.name,
        )

    def test_create_product_type_with_category(self):
        category = CategoryFactory.create()

        data = self.data | {"category_ids": [category.id]}
        response = self.client.post("/api/v1/producttypes/", data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().categories.first().name, category.name
        )

    def test_create_product_type_with_tag(self):
        tag = TagFactory.create()

        data = self.data | {"tag_ids": [tag.id]}
        response = self.client.post("/api/v1/producttypes/", data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().tags.first().name, tag.name)

    def test_create_product_type_with_condition(self):
        condition = ConditionFactory.create()

        data = self.data | {"condition_ids": [condition.id]}
        response = self.client.post("/api/v1/producttypes/", data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().conditions.first().name, condition.name
        )

    def test_update_minimal_product_type(self):
        product_type = ProductTypeFactory.create()

        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/", self.data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_related_type(self):
        related_product_type = ProductTypeFactory.create()
        product_type = ProductTypeFactory.create()

        data = self.data | {"related_product_types": [related_product_type.id]}
        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 2)
        self.assertEqual(
            ProductType.objects.get(id=product_type.id)
            .related_product_types.first()
            .name,
            related_product_type.name,
        )

    def test_update_product_type_with_category(self):
        product_type = ProductTypeFactory.create()
        category = CategoryFactory.create()

        data = self.data | {"category_ids": [category.id]}
        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().categories.first().name, category.name
        )

    def test_update_product_type_with_tag(self):
        product_type = ProductTypeFactory.create()
        tag = TagFactory.create()

        data = self.data | {"tag_ids": [tag.id]}

        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(product_type.tags.first().name, tag.name)

    def test_update_product_type_with_condition(self):
        product_type = ProductTypeFactory.create()
        condition = ConditionFactory.create()

        data = self.data | {"condition_ids": [condition.id]}
        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().conditions.first().name, condition.name
        )

    def test_add_question_to_product_type(self):
        product_type = ProductTypeFactory.create()

        data = {"question": "18?", "answer": "eligible"}
        response = self.client.post(
            f"/api/v1/producttypes/{product_type.id}/questions/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(product_type.questions.first().question, "18?")

    def test_add_field_to_product_type(self):
        product_type = ProductTypeFactory.create()

        data = {"name": "test field", "description": "test", "type": "textfield"}
        response = self.client.post(
            f"/api/v1/producttypes/{product_type.id}/fields/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().fields.first().name, "test field")

    def test_add_link_to_product_type(self):
        product_type = ProductTypeFactory.create()

        data = {"name": "test link", "url": "https://www.google.com"}

        response = self.client.post(
            f"/api/v1/producttypes/{product_type.id}/links/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(product_type.links.first().name, "test link")

    @freeze_time("2024-01-01")
    def test_add_price_to_product_type(self):
        product_type = ProductTypeFactory.create()

        data = {"valid_from": datetime.date(2024, 1, 2)}

        response = self.client.post(
            f"/api/v1/producttypes/{product_type.id}/prices/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Price.objects.count(), 1)
        self.assertEqual(product_type.prices.first().valid_from, data["valid_from"])

    @freeze_time("2024-01-01")
    def test_add_price_option_to_product_type(self):
        product_type = ProductTypeFactory.create()

        data = {
            "valid_from": datetime.date(2024, 1, 2),
            "options": [{"amount": "74.99", "description": "spoed"}],
        }

        response = self.client.post(
            f"/api/v1/producttypes/{product_type.id}/prices/", data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Price.objects.count(), 1)
        self.assertEqual(PriceOption.objects.count(), 1)
        self.assertEqual(
            product_type.prices.first().options.first().amount,
            Decimal("74.99"),
        )

    @freeze_time("2024-01-01")
    def test_remove_price_options(self):
        product_type = ProductTypeFactory.create()
        price = PriceFactory.create(
            product_type=product_type, valid_from=datetime.date(2024, 1, 2)
        )
        PriceOptionFactory.create(price=price)
        PriceOptionFactory.create(price=price)

        data = {
            "valid_from": price.valid_from,
            "options": [],
        }

        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/prices/{price.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Price.objects.count(), 1)
        self.assertEqual(PriceOption.objects.count(), 0)

    @freeze_time("2024-01-01")
    def test_update_and_delete_price_option(self):
        product_type = ProductTypeFactory.create()
        price = PriceFactory.create(
            product_type=product_type, valid_from=datetime.date(2024, 1, 2)
        )
        option_to_be_updated = PriceOptionFactory.create(price=price)
        PriceOptionFactory.create(price=price)

        data = {
            "valid_from": price.valid_from,
            "options": [
                {
                    "id": option_to_be_updated.id,
                    "amount": "20",
                    "description": option_to_be_updated.description,
                }
            ],
        }

        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/prices/{price.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Price.objects.count(), 1)
        self.assertEqual(PriceOption.objects.count(), 1)
        self.assertEqual(PriceOption.objects.first().amount, Decimal("20"))

    @freeze_time("2024-01-01")
    def test_create_and_delete_price_option(self):
        product_type = ProductTypeFactory.create()
        price = PriceFactory.create(
            product_type=product_type, valid_from=datetime.date(2024, 1, 2)
        )
        PriceOptionFactory.create(price=price)

        data = {
            "valid_from": price.valid_from,
            "options": [{"amount": "20", "description": "test"}],
        }

        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/prices/{price.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Price.objects.count(), 1)
        self.assertEqual(PriceOption.objects.count(), 1)
        self.assertEqual(PriceOption.objects.first().amount, Decimal("20"))

    @freeze_time("2024-01-01")
    def test_exception_when_option_not_part_of_price(self):
        product_type = ProductTypeFactory.create()
        price = PriceFactory.create(
            product_type=product_type, valid_from=datetime.date(2024, 1, 2)
        )

        option = PriceOptionFactory.create(price=PriceFactory.create())

        data = {
            "valid_from": price.valid_from,
            "options": [
                {"id": option.id, "amount": "20", "description": option.description}
            ],
        }

        response = self.client.put(
            f"/api/v1/producttypes/{product_type.id}/prices/{price.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
