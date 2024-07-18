import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

import pytz

from open_producten.producttypes.models import FieldTypes
from open_producten.producttypes.tests.factories import FieldFactory

from .factories import DataFactory


class TestData(TestCase):

    def test_format_number(self):
        field = FieldFactory.create(type=FieldTypes.NUMBER)

        data = DataFactory.create(field=field, data="5")
        self.assertEqual(data.format(), 5)

    def test_format_checkbox(self):
        field = FieldFactory.create(type=FieldTypes.CHECKBOX)

        data = DataFactory.create(field=field, data="true")
        self.assertEqual(data.format(), True)

        data = DataFactory.create(field=field, data="false")
        self.assertEqual(data.format(), False)

    def test_format_date(self):
        field = FieldFactory.create(type=FieldTypes.DATE)

        data = DataFactory.create(field=field, data="2024-07-16")
        self.assertEqual(data.format(), datetime.date(2024, 7, 16))

    def test_format_datetime(self):
        field = FieldFactory.create(type=FieldTypes.DATETIME)

        data = DataFactory.create(field=field, data="2024-07-11T12:04:03+02:00")
        tz = pytz.timezone("Europe/Amsterdam")

        self.assertEqual(
            data.format(), tz.localize(datetime.datetime(2024, 7, 11, 12, 4, 3))
        )

    def test_format_time(self):
        field = FieldFactory.create(type=FieldTypes.TIME)

        data = DataFactory.create(field=field, data="12:33:01")
        self.assertEqual(data.format(), datetime.time(12, 33, 1))

    def test_format_map(self):
        field = FieldFactory.create(type=FieldTypes.MAP)

        data = DataFactory.create(
            field=field, data="52.13309377014838,5.339086446962994"
        )
        self.assertEqual(data.format(), ["52.13309377014838", "5.339086446962994"])

    def test_format_select(self):
        field = FieldFactory.create(type=FieldTypes.SELECT)

        data = DataFactory.create(field=field, data="abc,def")
        self.assertEqual(data.format(), ["abc", "def"])

    def test_clean_bsn(self):
        field = FieldFactory.create(type=FieldTypes.BSN)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="1234").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abc").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="123456789").clean()

        DataFactory.build(field=field, data="111222333").clean()

    def test_clean_checkbox(self):
        field = FieldFactory.create(type=FieldTypes.CHECKBOX)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="1234").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data=True).clean()

        DataFactory.build(field=field, data="true").clean()
        DataFactory.build(field=field, data="false").clean()

    def test_clean_cosign(self):
        field = FieldFactory.create(type=FieldTypes.COSIGN)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde@").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde@gmail.").clean()

        DataFactory.build(field=field, data="abcde@gmail.com").clean()

    def test_clean_currency(self):
        field = FieldFactory.create(type=FieldTypes.CURRENCY)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="123a").clean()

        DataFactory.build(field=field, data="123124").clean()
        DataFactory.build(field=field, data="123124,12").clean()

    def test_clean_date(self):
        field = FieldFactory.create(type=FieldTypes.DATE)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abc").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="20240101").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="2024-13-01").clean()

        DataFactory.build(field=field, data="2024-01-01").clean()

    def test_clean_datetime(self):
        field = FieldFactory.create(type=FieldTypes.DATETIME)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abc").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="20241001").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="2023-13-01").clean()

        DataFactory.build(field=field, data="2024-01-01T13:00:00+02:00").clean()

    def test_clean_email(self):
        field = FieldFactory.create(type=FieldTypes.EMAIL)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="xyz@").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde@gmail.").clean()

        DataFactory.build(field=field, data="abcde@gmail.com").clean()

    def test_clean_file(self):  # TODO
        pass

    def test_clean_iban(self):  # TODO
        pass

    def test_clean_license_plate(self):
        field = FieldFactory.create(type=FieldTypes.LICENSE_PLATE)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abc123ad").clean()

        DataFactory.build(field=field, data="123-aaa-123").clean()

    def test_clean_map(self):
        field = FieldFactory.create(type=FieldTypes.MAP)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="42, 21").clean()

        DataFactory.build(field=field, data="42,12").clean()
        DataFactory.build(field=field, data="42.1294323,12.9283498").clean()

    def test_clean_number(self):
        field = FieldFactory.create(type=FieldTypes.NUMBER)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        DataFactory.build(field=field, data="42.12").clean()
        DataFactory.build(field=field, data="42.1294323").clean()

    def test_clean_phone_number(self):
        field = FieldFactory.create(type=FieldTypes.PHONE_NUMBER)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abcde").clean()

        DataFactory.build(field=field, data="0612165228").clean()
        DataFactory.build(field=field, data="+31 6 12 16 52 28").clean()

    def test_clean_postcode(self):
        field = FieldFactory.create(type=FieldTypes.POSTCODE)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="AB 3123").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="0334 AA").clean()

        DataFactory.build(field=field, data="3441ER").clean()
        DataFactory.build(field=field, data="3441 ER").clean()

    def test_clean_radio(self):
        field = FieldFactory.create(type=FieldTypes.RADIO, choices=["a", "b"])

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="d").clean()

        DataFactory.build(field=field, data="a").clean()
        DataFactory.build(field=field, data="b").clean()

    def test_clean_select(self):
        field = FieldFactory.create(type=FieldTypes.SELECT, choices=["a", "b"])

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="d,").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="d").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="a,d").clean()

        DataFactory.build(field=field, data="a").clean()
        DataFactory.build(field=field, data="a,b").clean()

    def test_clean_select_boxes(self):
        field = FieldFactory.create(type=FieldTypes.SELECT_BOXES, choices=["a", "b"])

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data=")(").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data='{"a": true}').clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data='{"a": true, "d": true}').clean()

        DataFactory.build(field=field, data='{"a": true, "b": true}').clean()

    def test_clean_signature(self):
        field = FieldFactory.create(type=FieldTypes.SIGNATURE)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="signature").clean()

        DataFactory.build(field=field, data="data:image/png;base64,A812EEAa").clean()

    def test_clean_time(self):
        field = FieldFactory.create(type=FieldTypes.TIME)

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="abc").clean()

        with self.assertRaises(ValidationError):
            DataFactory.build(field=field, data="120302").clean()

        DataFactory.build(field=field, data="12:00:00").clean()
