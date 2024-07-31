from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet

from open_producten.producttypes.models import (
    Category,
    Field,
    Link,
    Price,
    ProductType,
    Question,
)
from open_producten.producttypes.serializers.category import CategorySerializer
from open_producten.producttypes.serializers.children import (
    FieldSerializer,
    LinkSerializer,
    PriceSerializer,
    QuestionSerializer,
)
from open_producten.producttypes.serializers.producttype import ProductTypeSerializer


class BaseModelViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]


class ProductTypeViewSet(BaseModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    lookup_field = "id"


class ProductTypeChildViewSet(BaseModelViewSet):

    def get_queryset(self):
        return self.queryset.filter(product_type_id=self.kwargs["id"])

    def perform_create(self, serializer):
        serializer.save(
            product_type=get_object_or_404(ProductType, id=self.kwargs["id"])
        )


class ProductTypeLinkViewSet(ProductTypeChildViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class ProductTypePriceViewSet(ProductTypeChildViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer


class ProductTypeFieldViewSet(ProductTypeChildViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


class ProductTypeQuestionViewSet(ProductTypeChildViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "id"


class CategoryChildViewSet(BaseModelViewSet):

    def get_queryset(self):
        return self.queryset.filter(category_id=self.kwargs["id"])

    def perform_create(self, serializer):
        serializer.save(category=get_object_or_404(Category, id=self.kwargs["id"]))


class CategoryQuestionViewSet(CategoryChildViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
