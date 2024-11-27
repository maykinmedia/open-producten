from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.test import TestCase

from geopy.exc import GeopyError

from .factories import LocatieFactory


class TestLocatie(TestCase):

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_address(self):
        locatie = LocatieFactory.create(
            straat="Keizersgracht",
            huisnummer="117",
            postcode="1015 CJ",
            stad="Amsterdam",
        )
        self.assertEqual(locatie.address, "Keizersgracht 117, 1015CJ Amsterdam")

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(side_effect=GeopyError("geopy crashed")),
    )
    def test_clean_geometry_with_geopy_error(self):
        locatie = LocatieFactory.build()

        with self.assertRaisesMessage(
            ValidationError,
            "Het vinden van de coördinaten van de adresgegevens is mislukt: geopy crashed",
        ):
            locatie.clean_geometry()

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(side_effect=IndexError),
    )
    def test_clean_geometry_with_index_error(self):
        locatie = LocatieFactory.build()

        with self.assertRaisesMessage(
            ValidationError, "Er zijn geen adresgegevens gegeven."
        ):
            locatie.clean_geometry()

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=None),
    )
    def test_clean_geometry_with_none_point(self):
        locatie = LocatieFactory.build()

        with self.assertRaisesMessage(
            ValidationError,
            "Coördinaten van het adres kunnen niet worden gevonden. Zorg ervoor dat de adresgegevens correct zijn",
        ):
            locatie.clean_geometry()

    @patch(
        "open_producten.locaties.models.locatie.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_clean_geometry_with_valid_point(self):
        locatie = LocatieFactory.build()
        locatie.clean_geometry()

        self.assertEqual(locatie.coordinaten.coords, (4.84303667, 52.38559043))
