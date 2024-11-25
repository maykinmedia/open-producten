from unittest import TestCase

from ..serializers import build_array_duplicates_error_message


class Dummy:

    def __init__(self, id):
        self.id = id


class TestBuildArrayError(TestCase):

    def setUp(self):
        self.object_a = Dummy("a")
        self.object_b = Dummy("b")

    def test_build_array_error_should_return_errors_when_list_has_duplicate_object(
        self,
    ):
        errors = dict()
        object_list = [self.object_a, self.object_b, self.object_b]

        build_array_duplicates_error_message(object_list, "test", errors)

        self.assertEqual(errors, {"test": ["Duplicate Dummy id: b at index 2"]})

    def test_build_array_error_should_return_multiple_errors_when_list_has_multiple_duplicate_object(
        self,
    ):
        errors = dict()
        object_list = [self.object_a, self.object_b, self.object_b, self.object_b]

        build_array_duplicates_error_message(object_list, "test", errors)

        self.assertEqual(
            errors,
            {
                "test": [
                    "Duplicate Dummy id: b at index 2",
                    "Duplicate Dummy id: b at index 3",
                ]
            },
        )

    def test_build_array_error_should_not_return_errors_list_has_unique_values(self):
        errors = dict()
        object_list = [self.object_a, self.object_b]

        build_array_duplicates_error_message(object_list, "test", errors)
        self.assertEqual(errors, {})
