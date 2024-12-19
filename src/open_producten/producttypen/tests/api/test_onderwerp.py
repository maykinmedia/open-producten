from django.forms import model_to_dict
from django.urls import reverse

from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import Onderwerp, Vraag
from open_producten.producttypen.tests.factories import (
    OnderwerpFactory,
    ProductTypeFactory,
    VraagFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


def onderwerp_to_dict(onderwerp):
    onderwerp_dict = model_to_dict(onderwerp, exclude=("path", "depth", "numchild")) | {
        "id": str(onderwerp.id)
    }
    onderwerp_dict["vragen"] = [
        model_to_dict(vraag) for vraag in onderwerp.vragen.all()
    ]
    onderwerp_dict["product_typen"] = [
        model_to_dict(product_type) for product_type in onderwerp.product_typen.all()
    ]
    onderwerp_dict["aanmaak_datum"] = str(
        onderwerp.aanmaak_datum.astimezone().isoformat()
    )
    onderwerp_dict["update_datum"] = str(
        onderwerp.update_datum.astimezone().isoformat()
    )
    onderwerp_dict["hoofd_onderwerp"] = (
        onderwerp.hoofd_onderwerp.id if onderwerp.hoofd_onderwerp else None
    )

    return onderwerp_dict


class TestOnderwerpViewSet(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.data = {
            "naam": "test-onderwerp",
            "hoofd_onderwerp": None,
            "product_type_ids": [],
        }
        self.path = reverse("onderwerp-list")

    def test_read_onderwerp_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_minimal_onderwerp(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Onderwerp.objects.count(), 1)

    def test_create_onderwerp_with_hoofd_onderwerp(self):
        self.maxDiff = None
        hoofd_onderwerp = OnderwerpFactory.create()
        data = self.data | {"hoofd_onderwerp": hoofd_onderwerp.id}

        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Onderwerp.objects.count(), 2)

        onderwerp = Onderwerp.objects.get(id=response.data["id"])
        self.assertEqual(onderwerp.get_parent(), hoofd_onderwerp)
        self.assertEqual(response.data, onderwerp_to_dict(onderwerp))

    def test_create_onderwerp_with_product_type(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id]}

        response = self.post(data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Onderwerp.objects.count(), 1)
        self.assertEqual(
            list(Onderwerp.objects.values_list("product_typen", flat=True)),
            [product_type.id],
        )

    def test_create_hoofd_onderwerp_with_duplicate_product_typen_returns_error(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id, product_type.id]}

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {product_type.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_published_sub_onderwerp_with_unpublished_hoofd_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)

        data = self.data | {"hoofd_onderwerp": hoofd_onderwerp.id, "gepubliceerd": True}

        response = self.post(data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": ErrorDetail(
                    string="Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
                    code="invalid",
                )
            },
        )

    def test_update_change_from_root_to_hoofd_onderwerp(self):
        new_hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = OnderwerpFactory.create()

        data = self.data | {"hoofd_onderwerp": new_hoofd_onderwerp.id}
        response = self.put(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(onderwerp.get_parent(), new_hoofd_onderwerp)

    def test_update_change_from_hoofd_onderwerp_to_root(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = hoofd_onderwerp.add_child(naam="test-onderwerp")

        data = self.data | {"hoofd_onderwerp": None}
        response = self.put(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(onderwerp.get_parent(), None)

    def test_update_change_from_hoofd_onderwerp_to_hoofd_onderwerp(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = hoofd_onderwerp.add_child(naam="test-onderwerp")

        new_hoofd_onderwerp = OnderwerpFactory.create()

        data = self.data | {"hoofd_onderwerp": new_hoofd_onderwerp.id}
        response = self.put(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(onderwerp.get_parent(update=True), new_hoofd_onderwerp)

    def test_update_hoofd_onderwerp_with_duplicate_product_typen_returns_error(self):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_ids": [product_type.id, product_type.id]}

        response = self.put(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {product_type.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_unpublished_sub_onderwerp_to_published_with_unpublished_hoofd_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        sub_onderwerp = hoofd_onderwerp.add_child(naam="sub onderwerp")

        data = self.data | {"hoofd_onderwerp": hoofd_onderwerp.id, "gepubliceerd": True}

        response = self.put(sub_onderwerp.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": ErrorDetail(
                    string="Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
                    code="invalid",
                )
            },
        )

    def test_update_published_hoofd_onderwerp_to_unpublished_with_published_sub_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=True)
        hoofd_onderwerp.add_child(naam="sub onderwerp", gepubliceerd=True)

        data = self.data | {"hoofd_onderwerp": None, "gepubliceerd": False}

        response = self.put(hoofd_onderwerp.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": ErrorDetail(
                    string="Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben.",
                    code="invalid",
                )
            },
        )

    def test_partial_update(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = hoofd_onderwerp.add_child(naam="test-onderwerp")

        data = {"naam": "update"}
        response = self.patch(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(onderwerp.naam, "update")
        self.assertEqual(onderwerp.get_parent(), hoofd_onderwerp)

    def test_partial_update_change_hoofd_onderwerp(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = hoofd_onderwerp.add_child(naam="test-onderwerp")

        new_hoofd_onderwerp = OnderwerpFactory.create()

        data = {"hoofd_onderwerp": new_hoofd_onderwerp.id}
        response = self.patch(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(onderwerp.get_parent(update=True), new_hoofd_onderwerp)

    def test_partial_update_change_hoofd_onderwerp_to_root(self):
        hoofd_onderwerp = OnderwerpFactory.create()
        onderwerp = hoofd_onderwerp.add_child(naam="test-onderwerp")

        data = {"hoofd_onderwerp": None}
        response = self.patch(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(onderwerp.get_parent(update=True), None)

    def test_partial_update_hoofd_onderwerp_with_duplicate_product_typen_returns_error(
        self,
    ):
        onderwerp = OnderwerpFactory.create()
        product_type = ProductTypeFactory.create()
        data = {"product_type_ids": [product_type.id, product_type.id]}

        response = self.patch(onderwerp.id, data)

        onderwerp.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "product_type_ids": [
                    ErrorDetail(
                        string=f"Dubbel id: {product_type.id} op index 1.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_unpublished_sub_onderwerp_to_published_with_unpublished_hoofd_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        sub_onderwerp = hoofd_onderwerp.add_child(naam="sub onderwerp")

        data = {"gepubliceerd": True}

        response = self.patch(sub_onderwerp.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": ErrorDetail(
                    string="Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
                    code="invalid",
                )
            },
        )

    def test_partial_update_published_hoofd_onderwerp_to_unpublished_with_published_sub_onderwerp_returns_error(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=True)
        hoofd_onderwerp.add_child(naam="sub onderwerp", gepubliceerd=True)

        data = {"gepubliceerd": False}

        response = self.patch(hoofd_onderwerp.id, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "hoofd_onderwerp": ErrorDetail(
                    string="Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben.",
                    code="invalid",
                )
            },
        )

    def test_read_onderwerpen(self):
        onderwerp = OnderwerpFactory.create()

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [onderwerp_to_dict(onderwerp)])

    def test_read_onderwerp(self):
        onderwerp = OnderwerpFactory.create()

        response = self.get(onderwerp.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, onderwerp_to_dict(onderwerp))

    def test_delete_onderwerp(self):
        onderwerp = OnderwerpFactory.create()
        VraagFactory.create(onderwerp=onderwerp)

        response = self.delete(onderwerp.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Onderwerp.objects.count(), 0)
        self.assertEqual(Vraag.objects.count(), 0)
