from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from open_producten.producttypen.admin import OnderwerpAdmin
from open_producten.producttypen.models import Onderwerp
from open_producten.producttypen.tests.factories import (
    OnderwerpFactory,
    ProductTypeFactory,
)


class TestOnderwerpAdmin(TestCase):

    def setUp(self):
        self.admin = OnderwerpAdmin(Onderwerp, AdminSite())

    def test_get_deleted_objects_when_linked_product_type_has_one_onderwerp(self):
        product_type = ProductTypeFactory(naam="product type")
        product_type.onderwerpen.add(OnderwerpFactory(naam="onderwerp"))
        product_type.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Onderwerp.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Product Type <a href='/admin/producttypen/producttype/{product_type.id}/change/'>"
                f"product type</a> moet aan een minimaal één onderwerp zijn gelinkt. "
                f"Huidige onderwerpen: onderwerp."
            ],
        )

    def test_get_deleted_objects_when_linked_product_type_has_other_onderwerpen(self):
        onderwerp = OnderwerpFactory()
        product_type = ProductTypeFactory()
        product_type.onderwerpen.add(onderwerp)
        product_type.onderwerpen.add(OnderwerpFactory())
        product_type.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Onderwerp.objects.filter(id=onderwerp.id), self.client.request()
        )
        self.assertEqual(protected, [])

    def test_get_deleted_objects_with_multiple_onderwerpen(self):
        product_type = ProductTypeFactory(naam="product type")
        product_type.onderwerpen.add(OnderwerpFactory(naam="onderwerp"))
        product_type.onderwerpen.add(OnderwerpFactory(naam="onderwerp 2"))
        product_type.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Onderwerp.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Product Type <a href='/admin/producttypen/producttype/{product_type.id}/change/'>"
                f"product type</a> moet aan een minimaal één onderwerp zijn gelinkt. "
                f"Huidige onderwerpen: onderwerp, onderwerp 2."
            ],
        )
