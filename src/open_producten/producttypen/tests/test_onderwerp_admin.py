from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from django.test import TestCase

from open_producten.utils.tests.helpers import build_formset_data

from ..admin.onderwerp import OnderwerpAdmin, OnderwerpAdminFormSet
from ..models import Onderwerp


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
