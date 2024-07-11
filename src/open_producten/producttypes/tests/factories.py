import factory
from django.utils.text import slugify

from ..models import (
    Category,
    Condition,
    Price,
    PriceOption,
    ProductType,
    Question,
    Tag,
    Upn,
)


class UpnFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"upn {n}")
    url = factory.Faker("url")

    class Meta:
        model = Upn


class ProductTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"product {n}")
    slug = factory.LazyAttribute(lambda a: slugify(a.name))
    summary = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    published = True
    uniform_product_name = factory.SubFactory(UpnFactory)

    class Meta:
        model = ProductType

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.add(category)

    @factory.post_generation
    def related_products(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for related_product in extracted:
                self.related_products.add(related_product)


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"category {n}")
    slug = factory.LazyAttribute(lambda a: slugify(a.name))
    description = factory.Faker("sentence")
    published = True

    class Meta:
        model = Category

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """For now factory creates only root categories"""
        return Category.add_root(**kwargs)


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"tag {n}")
    slug = factory.LazyAttribute(lambda a: slugify(a.name))

    class Meta:
        model = Tag


class ConditionFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    question = factory.Faker("word")
    positive_text = factory.Faker("word")
    negative_text = factory.Faker("word")
    rule = factory.Faker("word")

    class Meta:
        model = Condition


class QuestionFactory(factory.django.DjangoModelFactory):
    question = factory.Faker("sentence")
    answer = factory.Faker("text")

    class Meta:
        model = Question


class PriceFactory(factory.django.DjangoModelFactory):
    start_date = factory.Faker("date")

    class Meta:
        model = Price


class PriceOptionFactory(factory.django.DjangoModelFactory):
    price = factory.Faker("price")
    description = factory.Faker("sentence")

    class Meta:
        model = PriceOption
