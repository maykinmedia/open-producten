import datetime
import uuid

from freezegun import freeze_time
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.products.models import Data, Product
from open_producten.products.tests.factories import DataFactory, ProductFactory
from open_producten.producttypes.models import Field, FieldTypes
from open_producten.producttypes.tests.factories import FieldFactory, ProductTypeFactory
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id


def product_to_dict(product):
    product_dict = model_to_dict_with_id(product)
    product_dict["start_date"] = str(product_dict["start_date"])
    product_dict["data"] = [
        model_to_dict_with_id(data, exclude=["product"])
        | {"field": model_to_dict_with_id(data.field, exclude=["product_type"])}
        for data in product.data.all()
    ]
    product_dict["end_date"] = str(product_dict["end_date"])
    product_dict["created_on"] = str(product.created_on.astimezone().isoformat())
    product_dict["updated_on"] = str(product.updated_on.astimezone().isoformat())

    product_dict["product_type"] = model_to_dict_with_id(
        product.product_type,
        exclude=(
            "categories",
            "conditions",
            "tags",
            "related_product_types",
            "contacts",
            "locations",
            "organisations",
        ),
    )
    product_dict["product_type"][
        "uniform_product_name"
    ] = product.product_type.uniform_product_name.uri

    product_dict["product_type"]["created_on"] = str(
        product.product_type.created_on.astimezone().isoformat()
    )
    product_dict["product_type"]["updated_on"] = str(
        product.product_type.updated_on.astimezone().isoformat()
    )
    product_dict["product_type"]["icon"] = None
    product_dict["product_type"]["image"] = None
    return product_dict


@freeze_time("2024-01-01")
class TestProduct(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.data = {
            "product_type_id": self.product_type.id,
            "bsn": "111222333",
            "start_date": datetime.date(2024, 1, 2),
            "end_date": datetime.date(2024, 12, 31),
            "data": [],
        }
        self.path = "/api/v1/products/"

    def test_read_product_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def _create_product(self):
        return ProductFactory.create(bsn="111222333")

    def test_create_product(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(response.data, product_to_dict(product))

    def test_create_product_without_bsn_or_kvk_returns_error(self):
        data = self.data.copy()
        data.pop("bsn")

        response = self.post(data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "non_field_errors": [
                    ErrorDetail(
                        string="A product must be linked to a bsn or kvk number (or both)",
                        code="invalid",
                    )
                ]
            },
        )
        self.assertEqual(Product.objects.count(), 0)

    def test_create_product_without_required_fields_returns_error(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )

        data = self.data | {"product_type_id": self.product_type.id}

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string=f"Missing required fields: {field.name}",
                        code="invalid",
                    )
                ]
            },
        )
        self.assertEqual(Product.objects.count(), 0)

    def test_create_product_without_non_required_fields(self):
        FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=False
        )

        data = self.data | {"product_type_id": self.product_type.id}

        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_with_data_for_required_field(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"field_id": field.id, "value": "abc"}],
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(Data.objects.count(), 1)

    def test_create_product_with_data_for_unrequired_field_returns_error(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=False
        )

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"field_id": field.id, "value": "abc"}],
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(Data.objects.count(), 1)

    def test_create_product_with_wrong_data_for_field_returns_error(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.NUMBER, is_required=True
        )

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"field_id": field.id, "value": "abc"}],
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string="Data at index 0: ['invalid number']",
                        code="invalid",
                    )
                ]
            },
        )
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Data.objects.count(), 0)

    def test_create_product_with_data_for_field_not_part_of_product_type_returns_error(
        self,
    ):
        field = FieldFactory.create(type=FieldTypes.TEXTFIELD, is_required=True)

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"field_id": field.id, "value": "abc"}],
        }

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string=f"field {field.name} is not part of {self.product_type.name}",
                        code="invalid",
                    )
                ]
            },
        )
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Data.objects.count(), 0)
        self.assertEqual(Field.objects.count(), 1)

    def test_update_product(self):
        product = self._create_product()

        data = self.data | {"end_date": datetime.date(2025, 12, 31)}
        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().end_date, data["end_date"])

    def test_update_product_without_bsn_or_kvk(self):
        product = self._create_product()

        data = self.data.copy()
        data.pop("bsn")
        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "non_field_errors": [
                    ErrorDetail(
                        string="A product must be linked to a bsn or kvk number (or both)",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_data(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )
        product = self._create_product()
        data_instance = DataFactory.create(product=product, field=field, value="abc")

        data = self.data | {"data": [{"id": data_instance.id, "value": "123"}]}

        response = self.put(product.id, data)
        data_instance.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Data.objects.count(), 1)
        self.assertEqual(data_instance.value, "123")

    def test_update_product_with_duplicate_data_ids_returns_error(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )
        product = self._create_product()
        data_instance = DataFactory.create(product=product, field=field, value="abc")

        data = self.data | {
            "data": [
                {"id": data_instance.id, "value": "123"},
                {"id": data_instance.id, "value": "123"},
            ]
        }

        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string=f"Duplicate data id: {data_instance.id} at index 1",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_with_data_not_part_of_product_returns_error(
        self,
    ):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )
        product = self._create_product()
        data_instance = DataFactory.create(
            product=self._create_product(), field=field, value="abc"
        )

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"id": data_instance.id, "value": "abc"}],
        }

        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string=f"Data id {data_instance.id} at index 0 is not part of product object",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_with_no_existing_data_object_returns_error(
        self,
    ):
        FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )
        product = self._create_product()

        dummy_id = uuid.uuid4()

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"id": dummy_id, "value": "abc"}],
        }

        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string=f"Data id {dummy_id} at index 0 does not exist",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_with_invalid_data_returns_error(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.NUMBER, is_required=True
        )
        product = self._create_product()
        data_instance = DataFactory.create(product=product, field=field, value="123")

        data = self.data | {
            "product_type_id": self.product_type.id,
            "data": [{"id": data_instance.id, "value": "abc"}],
        }

        response = self.put(product.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "data": [
                    ErrorDetail(
                        string="Data at index 0: ['invalid number']",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_product(self):
        product = self._create_product()

        data = {"end_date": datetime.date(2025, 12, 31)}
        response = self.patch(product.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)

    def test_partial_update_product_data(self):
        field = FieldFactory.create(
            product_type=self.product_type, type=FieldTypes.TEXTFIELD, is_required=True
        )
        product = self._create_product()
        data_instance = DataFactory.create(product=product, field=field, value="abc")

        data = {"data": [{"id": data_instance.id, "value": "123"}]}

        response = self.patch(product.id, data)
        data_instance.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Data.objects.count(), 1)
        self.assertEqual(data_instance.value, "123")

    def test_read_products(self):
        product = self._create_product()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [product_to_dict(product)])

    def test_read_product(self):
        product = self._create_product()

        response = self.get(product.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_to_dict(product))

    def test_read_product_with_data(self):
        product = self._create_product()
        field = FieldFactory.create(
            product_type=self.product_type, is_required=True, type="textfield"
        )
        DataFactory.create(product=product, field=field, value="abc")
        response = self.get(product.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, product_to_dict(product))

    def test_delete_product(self):
        product = self._create_product()
        response = self.delete(product.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)
