from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import OnderwerpFactory


class TestVraag(TestCase):

    def test_hoofd_onderwerpen_must_be_published_when_publishing_sub_onderwerp(self):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        sub_onderwerp = OnderwerpFactory.create(
            gepubliceerd=True, hoofd_onderwerp=hoofd_onderwerp
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Onderwerpen moeten gepubliceerd zijn voordat sub-onderwerpen kunnen worden gepubliceerd.",
        ):
            sub_onderwerp.clean()

        hoofd_onderwerp.gepubliceerd = True
        hoofd_onderwerp.save()

        sub_onderwerp.clean()

    def test_hoofd_onderwerpen_cannot_be_unpublished_with_published_sub_onderwerpen(
        self,
    ):
        hoofd_onderwerp = OnderwerpFactory.create(gepubliceerd=False)
        OnderwerpFactory.create(gepubliceerd=True, hoofd_onderwerp=hoofd_onderwerp)

        with self.assertRaisesMessage(
            ValidationError,
            "Onderwerpen kunnen niet ongepubliceerd worden als ze gepubliceerde sub-onderwerpen hebben.",
        ):
            hoofd_onderwerp.clean()
