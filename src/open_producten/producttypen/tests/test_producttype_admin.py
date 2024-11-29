from django.test import TestCase

from ..admin.producttype import ProductTypeAdminForm
from ..models import Onderwerp
from .factories import OnderwerpFactory, UniformeProductNaamFactory


class TestProductTypeAdminForm(TestCase):
    def setUp(self):
        upn = UniformeProductNaamFactory.create()
        self.data = {
            "naam": "test",
            "uniforme_product_naam": upn,
            "beschrijving": "beschrijving",
            "samenvatting": "samenvatting",
        }

    def test_at_least_one_onderwerp_is_required(self):
        form = ProductTypeAdminForm(data=self.data)

        self.assertEquals(
            form.errors, {"onderwerpen": ["Er is minimaal één onderwerp vereist."]}
        )

        OnderwerpFactory.create()
        form = ProductTypeAdminForm(
            data=self.data | {"onderwerpen": Onderwerp.objects.all()}
        )

        self.assertEquals(form.errors, {})
