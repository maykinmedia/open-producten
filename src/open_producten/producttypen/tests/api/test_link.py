from django.urls import reverse

from rest_framework.test import APIClient

from open_producten.producttypen.models import Link, ProductType
from open_producten.utils.tests.cases import BaseApiTestCase
from open_producten.utils.tests.helpers import model_to_dict_with_id

from ..factories import LinkFactory, ProductTypeFactory


def link_to_dict(link):
    link_dict = model_to_dict_with_id(link, exclude=["product_type"])
    link_dict["product_type_id"] = link.product_type.id

    return link_dict


class TestProductTypeLink(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        product_type = ProductTypeFactory.create()
        self.data = {
            "naam": "test link",
            "url": "https://www.google.com",
            "product_type_id": product_type.id,
        }
        self.path = reverse("link-list")

        self.link = LinkFactory.create(product_type=product_type)

    def test_read_link_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_create_link(self):
        response = self.post(self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Link.objects.count(), 2)

    def test_update_link(self):
        data = self.data | {"naam": "update"}
        response = self.put(self.link.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().links.first().naam, "update")

    def test_partial_update_link(self):
        data = {"naam": "update"}
        response = self.patch(self.link.id, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(ProductType.objects.first().links.first().naam, "update")

    def test_read_links(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"], [link_to_dict(self.link)])

    def test_read_link(self):
        response = self.get(self.link.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, link_to_dict(self.link))

    def test_delete_link(self):
        response = self.delete(self.link.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Link.objects.count(), 0)
