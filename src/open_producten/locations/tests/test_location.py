from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.test import TestCase

from geopy.exc import GeopyError

from .factories import LocationFactory


class TestLocation(TestCase):

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_address(self):
        location = LocationFactory.create(
            street="Keizersgracht",
            house_number="117",
            postcode="1015 CJ",
            city="Amsterdam",
        )
        self.assertEqual(location.address, "Keizersgracht 117, 1015CJ Amsterdam")

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(side_effect=GeopyError("geopy crashed")),
    )
    def test_clean_geometry_with_geopy_error(self):
        location = LocationFactory.build()

        with self.assertRaisesMessage(
            ValidationError, "Locating geo coordinates has failed: geopy crashed"
        ):
            location.clean_geometry()

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(side_effect=IndexError),
    )
    def test_clean_geometry_with_index_error(self):
        location = LocationFactory.build()

        with self.assertRaisesMessage(ValidationError, "No location data was provided"):
            location.clean_geometry()

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=None),
    )
    def test_clean_geometry_with_none_point(self):
        location = LocationFactory.build()

        with self.assertRaisesMessage(
            ValidationError,
            "Geo coordinates of the address can't be found. Make sure that the address data are correct",
        ):
            location.clean_geometry()

    @patch(
        "open_producten.locations.models.location.geocode_address",
        new=Mock(return_value=Point((4.84303667, 52.38559043))),
    )
    def test_clean_geometry_with_valid_point(self):
        location = LocationFactory.build()
        location.clean_geometry()

        self.assertEqual(location.coordinates.coords, (4.84303667, 52.38559043))
