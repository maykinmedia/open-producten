from unittest.mock import Mock, patch

from django.test import TestCase

from geopy.location import Location

from open_producten.utils.geocode import PdocLocatieserver, geocode_address


class TestGeocode(TestCase):

    def setUp(self):
        self.locatieServer = PdocLocatieserver()

        self.geocode_call_method = (
            "open_producten.utils.geocode.PdocLocatieserver._call_geocoder"
        )

        self.geocode_example_response = {
            "response": {
                "docs": [
                    {
                        "bron": "BAG",
                        "centroide_ll": "POINT(4.84303667 52.38559043)",
                        "id": "adr-54579b09efb5d1965ba24bbadcb81a52",
                        "rdf_seealso": "http://bag.basisregistraties.overheid.nl/bag/id/nummeraanduiding/0363200000483631",
                        "weergavenaam": "Kingsfordweg 151, 1043GR Amsterdam",
                    },
                    {
                        "bron": "BAG",
                        "centroide_ll": "POINT(4.84303667 52.38559043)",
                        "id": "adr-9b1f4ee2d066c3e80a55f8d1639e7d34",
                        "rdf_seealso": "http://bag.basisregistraties.overheid.nl/bag/id/nummeraanduiding/0363200000483632",
                        "weergavenaam": "Kingsfordweg 153, 1043GR Amsterdam",
                    },
                ],
                "maxScore": 12.828169,
                "numFound": 9299,
                "numFoundExact": True,
                "start": 0,
            }
        }

    def test_parse_json_with_valid_result(self):
        location = self.locatieServer._parse_json(self.geocode_example_response)
        self.assertEqual(location.address, "Kingsfordweg 151, 1043GR Amsterdam")
        self.assertEqual(location.longitude, 4.84303667)
        self.assertEqual(location.latitude, 52.38559043)

    def test_parse_json_with_invalid_result(self):
        location = self.locatieServer._parse_json(None)
        self.assertEqual(location, None)

    @patch(
        "open_producten.utils.geocode.PdocLocatieserver.geocode",
        new=Mock(
            return_value=Location(
                "Kingsfordweg 151, 1043GR Amsterdam", (4.84303667, 52.38559043), "dummy"
            )
        ),
    )
    def test_geocode_address(self):
        point = geocode_address("Kingsfordweg 151, 1043GR Amsterdam")

        self.assertEqual(point.x, 52.38559043)
        self.assertEqual(point.y, 4.84303667)

    @patch(
        "open_producten.utils.geocode.PdocLocatieserver.geocode",
        new=Mock(return_value=None),
    )
    def test_geocode_address_with_invalid_adress(self):
        point = geocode_address("Kingsfordweg 151, 1043GR Amsterdam")

        self.assertEqual(point, None)
