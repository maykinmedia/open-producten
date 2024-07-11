from datetime import datetime, timezone

from django.test import TestCase

from freezegun import freeze_time

from .factories import ConditionFactory


class TestBaseModel(TestCase):
    @freeze_time("2024-01-01")
    def setUp(self):
        self.model = ConditionFactory()
        self.model.save()

    def test_created_on_is_set(self):
        self.assertEqual(
            self.model.created_on, datetime(2024, 1, 1, tzinfo=timezone.utc)
        )

    def test_updated_on_is_set(self):
        self.model.save()
        self.assertNotEqual(
            self.model.updated_on, datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
