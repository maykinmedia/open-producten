import os
from io import StringIO
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase

from open_producten.producttypen.management.parsers import CsvParser
from open_producten.producttypen.models import UniformeProductNaam


class TestLoadUPNCommand(TestCase):

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "load_upl",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_load_csv_with_correct_columns(self):
        file_name = "data/upl.csv"
        path = os.path.join(os.path.dirname(__file__), file_name)
        result = self.call_command(path)
        self.assertEqual(result, f"Importing upn from {path}...\nDone (1 objects).\n")
        self.assertEqual(UniformeProductNaam.objects.count(), 1)
        self.assertEqual(
            UniformeProductNaam.objects.first().naam, "aangifte vertrek buitenland"
        )
        self.assertEqual(
            UniformeProductNaam.objects.first().uri,
            "http://standaarden.overheid.nl/owms/terms/AangifteVertrekBuitenland",
        )

    def test_load_csv_with_incorrect_columns(self):
        file_name = "data/wrong-upl.csv"
        path = os.path.join(os.path.dirname(__file__), file_name)

        with self.assertRaisesMessage(CommandError, "'URI' does not exist in csv"):
            self.call_command(path)


class TestCSVParser(SimpleTestCase):

    def setUp(self):
        self.parser = CsvParser()

    def test_parser_returns_error_when_format_is_not_csv(self):
        with self.assertRaisesMessage(Exception, "File format is not csv"):
            self.parser.parse("abc.txt")

    @patch("open_producten.producttypen.management.parsers.NamedTemporaryFile")
    @patch("open_producten.producttypen.management.parsers.CsvParser.process_csv")
    def test_parser_with_url(self, mock_process_csv, mock_NamedTemporaryFile):
        self.parser.parse("https://www.abc.com/abc.csv")

        self.assertEqual(mock_NamedTemporaryFile.call_count, 1)
        self.assertEqual(mock_process_csv.call_count, 1)

    @patch("tempfile.NamedTemporaryFile")
    @patch("open_producten.producttypen.management.parsers.CsvParser.process_csv")
    def test_parser_with_file(self, mock_process_csv, mock_NamedTemporaryFile):
        self.parser.parse("abc.csv")

        self.assertEqual(mock_NamedTemporaryFile.call_count, 0)
        self.assertEqual(mock_process_csv.call_count, 1)

    def test_process_csv(self):
        file_name = "data/upl.csv"
        path = os.path.join(os.path.dirname(__file__), file_name)
        result = self.parser.process_csv(path)
        self.assertEqual(
            result,
            [
                {
                    "Aanvraag": "",
                    "Autonomie": "",
                    "Bedrijf": "",
                    "Burger": "X",
                    "Dienstenwet": "",
                    "Gemeente": "X",
                    "Grondslag": "http://standaarden.overheid.nl/owms/terms/Wet_BRP_art_2_43",
                    "Grondslaglabel": "Artikel 2.43 Wet basisregistratie personen",
                    "Grondslaglink": "https://wetten.overheid.nl/jci1.3:c:BWBR0033715&hoofdstuk=2&afdeling=1&paragraaf=5&artikel=2.43",
                    "Medebewind": "X",
                    "Melding": "",
                    "Provincie": "",
                    "Rijk": "X",
                    "SDG": "D1",
                    "Subsidie": "",
                    "URI": "http://standaarden.overheid.nl/owms/terms/AangifteVertrekBuitenland",
                    "UniformeProductnaam": "aangifte vertrek buitenland",
                    "Verplichting": "X",
                    "Waterschap": "",
                }
            ],
        )
