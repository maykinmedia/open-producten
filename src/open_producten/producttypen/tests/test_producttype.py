from datetime import date

from django.test import TestCase

from freezegun import freeze_time

# from ...locations.tests.factories import ContactFactory
from .factories import PrijsFactory, ProductTypeFactory


class TestProductType(TestCase):
    def setUp(self):
        self.product_type = ProductTypeFactory.create()
        self.past_price = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=date(2020, 1, 1)
        )
        self.current_price = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=date(2024, 1, 1)
        )
        self.future_price = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=date(2025, 1, 1)
        )

    @freeze_time("2024-02-02")
    def test_current_price_when_set(self):
        price = self.product_type.current_price
        self.assertEqual(price, self.current_price)

    def test_current_price_without_prices(self):
        self.product_type = ProductTypeFactory.create()
        self.assertIsNone(self.product_type.current_price)

    # def test_clean_with_contact_that_has_no_org(self):
    #     contact = ContactFactory(organisation_id=None)
    #     product_type = ProductTypeFactory.create()
    #     product_type.contacts.add(contact)
    #     product_type.clean()
    #
    # def test_clean_with_contact_that_has_org(self):
    #     contact = ContactFactory()
    #     product_type = ProductTypeFactory.create()
    #     product_type.contacts.add(contact)
    #     product_type.clean()
    #
    #     self.assertEqual(product_type.organisations.count(), 1)
    #     self.assertEqual(product_type.organisations.first().id, contact.organisation.id)
