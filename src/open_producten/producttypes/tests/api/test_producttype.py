from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.forms import model_to_dict

from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.locations.tests.factories import (
    ContactFactory,
    LocationFactory,
    OrganisationFactory,
)
from open_producten.producttypes.models import Link, ProductType, Tag
from open_producten.producttypes.tests.factories import (
    CategoryFactory,
    ConditionFactory,
    LinkFactory,
    ProductTypeFactory,
    TagFactory,
    UniformProductNameFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id


def product_type_to_dict(product_type):
    product_type_dict = model_to_dict_with_id(product_type)
    product_type_dict["questions"] = [
        model_to_dict(question) for question in product_type.questions.all()
    ]
    product_type_dict["fields"] = [
        model_to_dict(field) for field in product_type.fields.all()
    ]
    product_type_dict["prices"] = [
        model_to_dict(price) for price in product_type.prices.all()
    ]
    product_type_dict["links"] = [
        model_to_dict(link) for link in product_type.links.all()
    ]
    product_type_dict["files"] = [
        model_to_dict(file) for file in product_type.files.all()
    ]

    product_type_dict["categories"] = []
    for category in product_type.categories.all():
        category_dict = model_to_dict_with_id(
            category, exclude=("path", "depth", "numchild")
        )
        category_dict["icon"] = None
        category_dict["image"] = None
        category_dict["created_on"] = str(category.created_on.astimezone().isoformat())
        category_dict["updated_on"] = str(category.updated_on.astimezone().isoformat())
        product_type_dict["categories"].append(category_dict)

    product_type_dict["created_on"] = str(
        product_type.created_on.astimezone().isoformat()
    )
    product_type_dict["updated_on"] = str(
        product_type.updated_on.astimezone().isoformat()
    )
    product_type_dict["uniform_product_name"] = product_type.uniform_product_name.uri
    product_type_dict["icon"] = None
    product_type_dict["image"] = None
    return product_type_dict


class TestProducttypeViewSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        upn = UniformProductNameFactory.create()
        category = CategoryFactory()

        self.data = {
            "name": "test-product-type",
            "summary": "test",
            "content": "test test",
            "uniform_product_name": upn.uri,
            "category_ids": [category.id],
        }

        self.path = "/api/v1/producttypes/"

    def test_read_product_type_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_minimal_product_type(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        product_type = ProductType.objects.first()
        self.assertEqual(response.data, product_type_to_dict(product_type))

    def test_create_product_type_without_fields_returns_error(self):
        data = self.data.copy()
        data["category_ids"] = []
        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "category_ids": [
                    ErrorDetail(
                        string="At least one category is required", code="invalid"
                    )
                ]
            },
        )

    def test_create_product_type_with_related_type(self):
        product_type = ProductTypeFactory.create()

        data = self.data | {"related_product_types": [product_type.id]}
        response = self.post(data)

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
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("categories__name", flat=True)),
            [category.name],
        )

    def test_create_product_type_with_tag(self):
        tag = TagFactory.create()

        data = self.data | {"tag_ids": [tag.id]}
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("tags__name", flat=True)), [tag.name]
        )

    def test_create_product_type_with_condition(self):
        condition = ConditionFactory.create()

        data = self.data | {"condition_ids": [condition.id]}
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("conditions__name", flat=True)),
            [condition.name],
        )

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_create_product_type_with_location(self):
        location = LocationFactory.create()

        data = self.data | {"location_ids": [location.id]}
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locations__name", flat=True)),
            [location.name],
        )

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_create_product_type_with_organisation(self):
        organisation = OrganisationFactory.create()

        data = self.data | {"organisation_ids": [organisation.id]}
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisations__name", flat=True)),
            [organisation.name],
        )

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_create_product_type_with_contact(self):
        contact = ContactFactory.create()

        data = self.data | {"contact_ids": [contact.id]}
        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacts__first_name", flat=True)),
            [contact.first_name],
        )

    def test_create_product_type_with_duplicate_ids_returns_error(self):
        tag = TagFactory.create()
        condition = ConditionFactory.create()
        category = CategoryFactory.create()
        related_product_type = ProductTypeFactory.create()

        data = self.data | {
            "category_ids": [category.id, category.id],
            "condition_ids": [condition.id, condition.id],
            "tag_ids": [tag.id, tag.id],
            "related_product_types": [related_product_type.id, related_product_type.id],
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "category_ids": [
                    ErrorDetail(
                        string=f"Duplicate Category id: {category.id} at index 1",
                        code="invalid",
                    )
                ],
                "condition_ids": [
                    ErrorDetail(
                        string=f"Duplicate Condition id: {condition.id} at index 1",
                        code="invalid",
                    )
                ],
                "related_product_types": [
                    ErrorDetail(
                        string=f"Duplicate ProductType id: {related_product_type.id} at index 1",
                        code="invalid",
                    )
                ],
                "tag_ids": [
                    ErrorDetail(
                        string=f"Duplicate Tag id: {tag.id} at index 1", code="invalid"
                    )
                ],
            },
        )

    def test_update_minimal_product_type(self):
        product_type = ProductTypeFactory.create()

        response = self.put(product_type.id, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_related_type(self):
        related_product_type = ProductTypeFactory.create()
        product_type = ProductTypeFactory.create()

        data = self.data | {"related_product_types": [related_product_type.id]}
        response = self.put(product_type.id, data)

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
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("categories__name", flat=True)),
            [category.name],
        )

    def test_update_product_type_with_tag(self):
        product_type = ProductTypeFactory.create()
        tag = TagFactory.create()

        data = self.data | {"tag_ids": [tag.id]}
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("tags__name", flat=True)), [tag.name]
        )

    def test_update_product_type_with_condition(self):
        product_type = ProductTypeFactory.create()
        condition = ConditionFactory.create()

        data = self.data | {"condition_ids": [condition.id]}
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("conditions__name", flat=True)),
            [condition.name],
        )

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_update_product_type_with_location(self):
        product_type = ProductTypeFactory.create()
        location = LocationFactory.create()

        data = self.data | {"location_ids": [location.id]}
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locations__name", flat=True)),
            [location.name],
        )

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_update_product_type_with_organisation(self):
        product_type = ProductTypeFactory.create()
        organisation = OrganisationFactory.create()

        data = self.data | {"organisation_ids": [organisation.id]}
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisations__name", flat=True)),
            [organisation.name],
        )

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_update_product_type_with_contact(self):
        product_type = ProductTypeFactory.create()
        contact = ContactFactory.create()

        data = self.data | {"contact_ids": [contact.id]}
        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacts__first_name", flat=True)),
            [contact.first_name],
        )

    def test_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        tag = TagFactory.create()
        condition = ConditionFactory.create()
        category = CategoryFactory.create()
        related_product_type = ProductTypeFactory.create()

        data = self.data | {
            "category_ids": [category.id, category.id],
            "condition_ids": [condition.id, condition.id],
            "tag_ids": [tag.id, tag.id],
            "related_product_types": [related_product_type.id, related_product_type.id],
        }

        response = self.put(product_type.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "category_ids": [
                    ErrorDetail(
                        string=f"Duplicate Category id: {category.id} at index 1",
                        code="invalid",
                    )
                ],
                "condition_ids": [
                    ErrorDetail(
                        string=f"Duplicate Condition id: {condition.id} at index 1",
                        code="invalid",
                    )
                ],
                "related_product_types": [
                    ErrorDetail(
                        string=f"Duplicate ProductType id: {related_product_type.id} at index 1",
                        code="invalid",
                    )
                ],
                "tag_ids": [
                    ErrorDetail(
                        string=f"Duplicate Tag id: {tag.id} at index 1", code="invalid"
                    )
                ],
            },
        )

    def test_partial_update_product_type(self):
        product_type = ProductTypeFactory.create()

        condition = ConditionFactory.create()
        tag = TagFactory.create()

        product_type.conditions.add(condition)
        product_type.tags.add(tag)
        product_type.save()

        data = {"name": "updated"}

        response = self.patch(product_type.id, data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(product_type.conditions.count(), 1)
        self.assertEqual(product_type.tags.count(), 1)
        self.assertEqual(product_type.name, "updated")

    def test_partial_update_product_type_delete_condition(self):
        product_type = ProductTypeFactory.create()
        condition = ConditionFactory.create()
        product_type.conditions.add(condition)
        product_type.save()

        data = {"name": "updated", "condition_ids": []}

        response = self.patch(product_type.id, data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(product_type.conditions.count(), 0)
        self.assertEqual(product_type.name, "updated")

    def test_partial_update_product_type_add_condition(self):
        product_type = ProductTypeFactory.create()
        condition = ConditionFactory.create()

        data = {"name": "updated", "condition_ids": [condition.id]}

        response = self.patch(product_type.id, data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(product_type.conditions.count(), 1)

    def test_partial_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        tag = TagFactory.create()
        condition = ConditionFactory.create()
        category = CategoryFactory.create()
        related_product_type = ProductTypeFactory.create()

        data = {
            "category_ids": [category.id, category.id],
            "condition_ids": [condition.id, condition.id],
            "tag_ids": [tag.id, tag.id],
            "related_product_types": [related_product_type.id, related_product_type.id],
        }

        response = self.patch(product_type.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "category_ids": [
                    ErrorDetail(
                        string=f"Duplicate Category id: {category.id} at index 1",
                        code="invalid",
                    )
                ],
                "condition_ids": [
                    ErrorDetail(
                        string=f"Duplicate Condition id: {condition.id} at index 1",
                        code="invalid",
                    )
                ],
                "related_product_types": [
                    ErrorDetail(
                        string=f"Duplicate ProductType id: {related_product_type.id} at index 1",
                        code="invalid",
                    )
                ],
                "tag_ids": [
                    ErrorDetail(
                        string=f"Duplicate Tag id: {tag.id} at index 1", code="invalid"
                    )
                ],
            },
        )

    def test_read_product_types(self):
        product_type = ProductTypeFactory.create()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [product_type_to_dict(product_type)])

    def test_read_product_type(self):
        product_type = ProductTypeFactory.create()

        response = self.get(product_type.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_type_to_dict(product_type))

    def test_delete_product_type(self):
        tag = TagFactory.create()
        product_type = ProductTypeFactory.create()
        product_type.tags.add(tag)
        product_type.save()
        LinkFactory.create(product_type=product_type)

        response = self.delete(product_type.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(ProductType.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Link.objects.count(), 0)
