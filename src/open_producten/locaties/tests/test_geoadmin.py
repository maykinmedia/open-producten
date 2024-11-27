from django.contrib.admin import AdminSite
from django.http import HttpRequest
from django.test import TestCase

from open_producten.locaties.admin import LocatieAdmin
from open_producten.locaties.models import Locatie
from open_producten.locaties.tests.factories import LocatieFactory


class TestGeoAdminMixin(TestCase):

    def setUp(self):
        site = AdminSite()
        self.admin = LocatieAdmin(Locatie, site)

    def test_get_read_only_fields_when_creating_object(self):
        read_only_fields = self.admin.get_readonly_fields(HttpRequest())
        self.assertIn("coordinaten", read_only_fields)

    def test_get_read_only_fields_when_updating_object(self):
        read_only_fields = self.admin.get_readonly_fields(
            HttpRequest(), LocatieFactory()
        )
        self.assertNotIn("coordinaten", read_only_fields)

    def test_form_when_creating_object(self):
        form_class = self.admin.get_form(HttpRequest())
        form = form_class()
        self.assertNotIn("coordinaten", form.fields)

    def test_form_when_updating_object(self):
        form_class = self.admin.get_form(HttpRequest(), LocatieFactory())
        form = form_class()
        self.assertIn("coordinaten", form.fields)
        self.assertTrue(form.fields["coordinaten"].disabled)
