from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from django.test import TestCase

from open_producten.utils.tests.helpers import build_formset_data

from ..admin.onderwerp import OnderwerpAdmin, OnderwerpAdminForm, OnderwerpAdminFormSet
from ..models import Onderwerp
from .factories import OnderwerpFactory


def create_form(data, instance=None):
    return OnderwerpAdminForm(
        instance=instance,
        data=data,
    )


class TestOnderwerpAdminForm(TestCase):

    def setUp(self):
        self.data = {
            "naam": "test",
            "_position": "first-child",
            "path": "00010001",
            "numchild": 1,
            "depth": 1,
        }

    def test_hoofd_onderwerpen_must_be_published_when_publishing_sub_onderwerp(self):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        data = self.data | {"gepubliceerd": True, "_ref_node_id": hoofd_onderwerp.id}

        form = create_form(data)

        self.assertEquals(
            form.non_field_errors(),
            [
                "Hoofd-onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd."
            ],
        )

        hoofd_onderwerp.gepubliceerd = True
        hoofd_onderwerp.save()

        form = create_form(data)
        self.assertEquals(form.errors, {})

    def test_hoofd_onderwerpen_cannot_be_published_with_published_sub_onderwerpen(self):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        hoofd_onderwerp.add_child(**{"naam": "sub onderwerp", "gepubliceerd": True})
        data = {"gepubliceerd": False, "_ref_node_id": None}

        form = create_form(data, hoofd_onderwerp)

        self.assertEquals(
            form.non_field_errors(),
            [
                "Hoofd-onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben."
            ],
        )


class TestOnderwerpAdminFormSet(TestCase):

    def setUp(self):
        self.formset = modelformset_factory(
            model=Onderwerp,
            formset=OnderwerpAdminFormSet,
            fields=OnderwerpAdmin.list_editable,
        )

        self.hoofd_onderwerp = Onderwerp.add_root(
            **{"naam": "hoofd onderwerp", "gepubliceerd": False}
        )
        self.sub_onderwerp = self.hoofd_onderwerp.add_child(
            **{"naam": "sub onderwerp", "gepubliceerd": True}
        )

    def test_hoofd_onderwerpen_cannot_be_unpublished_with_published_sub_onderwerpen(
        self,
    ):
        data = build_formset_data(
            "form",
            {
                "id": self.hoofd_onderwerp.id,  # gepubliceerd false
            },
            {"id": self.sub_onderwerp.id, "gepubliceerd": "on"},
        )

        object_formset = self.formset(data)

        with self.assertRaises(ValidationError):
            object_formset.clean()
