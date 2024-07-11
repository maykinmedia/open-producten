import factory

from ..models import (
    Category,
    Condition,
    Field,
    Price,
    PriceOption,
    ProductType,
    Question,
    Tag,
    UniformProductName,
)


class UniformProductNameFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"upn {n}")
    url = factory.Faker("url")

    class Meta:
        model = UniformProductName


class ProductTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"product type {n}")
    summary = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    published = True
    uniform_product_name = factory.SubFactory(UniformProductNameFactory)

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
    def related_product_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for related_product_type in extracted:
                self.related_product_types.add(related_product_type)


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"category {n}")
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

    class Meta:
        model = Tag


class ConditionFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    question = factory.Faker("word")
    positive_text = factory.Faker("word")
    negative_text = factory.Faker("word")

    class Meta:
        model = Condition


class QuestionFactory(factory.django.DjangoModelFactory):
    question = factory.Faker("sentence")
    answer = factory.Faker("text")

    class Meta:
        model = Question


class PriceFactory(factory.django.DjangoModelFactory):
    valid_from = factory.Faker("date")
    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Price


class PriceOptionFactory(factory.django.DjangoModelFactory):
    price = factory.Faker("price")
    description = factory.Faker("sentence")

    class Meta:
        model = PriceOption


class FieldFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"field {n}")
    description = factory.Faker("sentence")
    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Field
