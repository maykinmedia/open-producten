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

    def test_parent_nodes_must_be_published_when_publishing_child(self):
        parent = OnderwerpFactory.create(gepubliceerd=False)
        data = self.data | {"gepubliceerd": True, "_ref_node_id": parent.id}

        form = create_form(data)

        self.assertEquals(
            form.non_field_errors(),
            [
                "Hoofd-onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd."
            ],
        )

        parent.gepubliceerd = True
        parent.save()

        form = create_form(data)
        self.assertEquals(form.errors, {})

    def test_parent_nodes_cannot_be_published_with_published_children(self):
        parent = OnderwerpFactory.create(gepubliceerd=False)
        parent.add_child(**{"naam": "child", "gepubliceerd": True})
        data = {"gepubliceerd": False, "_ref_node_id": None}

        form = create_form(data, parent)

        self.assertEquals(
            form.non_field_errors(),
            [
                "Hoofd-onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben."
            ],
        )


class TestCategoryAdminFormSet(TestCase):

    def setUp(self):
        self.formset = modelformset_factory(
            model=Onderwerp,
            formset=OnderwerpAdminFormSet,
            fields=OnderwerpAdmin.list_editable,
        )

        self.parent = Onderwerp.add_root(**{"naam": "parent", "gepubliceerd": False})
        self.child = self.parent.add_child(**{"naam": "child", "gepubliceerd": True})

    def test_parent_nodes_cannot_be_unpublished_with_published_children(self):
        data = build_formset_data(
            "form",
            {
                "id": self.parent.id,  # gepubliceerd off
            },
            {"id": self.child.id, "gepubliceerd": "on"},
        )

        object_formset = self.formset(data)

        with self.assertRaises(ValidationError):
            object_formset.clean()
