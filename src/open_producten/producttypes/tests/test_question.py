from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import CategoryFactory, ProductTypeFactory, QuestionFactory


class TestQuestion(TestCase):

    def setUp(self):
        self.productType = ProductTypeFactory.create()
        self.category = CategoryFactory.create()
        pass

    def test_error_when_linked_to_type_and_category(self):
        question = QuestionFactory.build(
            product_type=self.productType, category=self.category
        )

        with self.assertRaises(ValidationError):
            question.clean()

    def test_error_when_not_linked_to_type_or_category(self):
        question = QuestionFactory.build()

        with self.assertRaises(ValidationError):
            question.clean()
