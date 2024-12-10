from datetime import date, timedelta
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.test import TestCase

from freezegun import freeze_time

from open_producten.producttypen.admin import PrijsAdmin
from open_producten.producttypen.models import Prijs

from ...accounts.tests.factories import UserFactory
from .factories import PrijsFactory, PrijsOptieFactory, ProductTypeFactory


class TestPrijs(TestCase):

    def test_unique_validation(self):
        product_type = ProductTypeFactory.create()
        PrijsFactory.create(
            product_type=product_type, actief_vanaf=date.today() + timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            duplicate = PrijsFactory.build(
                product_type=product_type, actief_vanaf=date.today() + timedelta(days=1)
            )
            duplicate.full_clean()

    def test_min_date_validation(self):
        with self.assertRaises(ValidationError):
            prijs = PrijsFactory.build(actief_vanaf=date(2020, 1, 1))
            prijs.full_clean()

    @freeze_time("2024-01-02")
    def test_change_permission_on_old_price(self):
        instance = PrijsFactory.create(actief_vanaf=date(2024, 1, 1))
        admin = PrijsAdmin(Prijs, AdminSite())
        request = self.client.request()
        request.user = UserFactory(superuser=True)

        self.assertFalse(admin.has_change_permission(request, instance))

    @freeze_time("2024-01-02")
    def test_change_permission_on_future_price(self):
        instance = PrijsFactory.create(actief_vanaf=date(2024, 3, 1))
        admin = PrijsAdmin(Prijs, AdminSite())
        request = self.client.request()
        request.user = UserFactory(superuser=True)

        self.assertTrue(admin.has_change_permission(request, instance))

    @freeze_time("2024-01-02")
    def test_change_permission_on_current_price(self):
        instance = PrijsFactory.create(actief_vanaf=date(2024, 1, 2))
        admin = PrijsAdmin(Prijs, AdminSite())
        request = self.client.request()
        request.user = UserFactory(superuser=True)

        self.assertTrue(admin.has_change_permission(request, instance))


class TestPrijsOptie(TestCase):
    def setUp(self):
        self.prijs = PrijsFactory.create()

    def test_min_amount_validation(self):
        with self.assertRaises(ValidationError):
            optie = PrijsOptieFactory.build(prijs=self.prijs, bedrag=Decimal("-1"))
            optie.full_clean()

    def test_decimal_place_validation(self):
        with self.assertRaises(ValidationError):
            optie = PrijsOptieFactory.build(prijs=self.prijs, bedrag=Decimal("0.001"))
            optie.full_clean()
