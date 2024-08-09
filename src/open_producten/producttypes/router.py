from rest_framework.routers import DefaultRouter

from open_producten.producttypes.views import (
    CategoryQuestionViewSet,
    CategoryViewSet,
    ProductTypeFieldViewSet,
    ProductTypeLinkViewSet,
    ProductTypePriceViewSet,
    ProductTypeQuestionViewSet,
    ProductTypeViewSet,
)

ProductTypesRouter = DefaultRouter()
ProductTypesRouter.register("producttypes", ProductTypeViewSet, basename="producttype")
ProductTypesRouter.register(
    "producttypes/(?P<product_type_id>[^/.]+)/links",
    ProductTypeLinkViewSet,
    basename="producttype-link",
)
ProductTypesRouter.register(
    "producttypes/(?P<product_type_id>[^/.]+)/prices",
    ProductTypePriceViewSet,
    basename="producttype-price",
)
ProductTypesRouter.register(
    "producttypes/(?P<product_type_id>[^/.]+)/questions",
    ProductTypeQuestionViewSet,
    basename="producttype-question",
)
ProductTypesRouter.register(
    "producttypes/(?P<product_type_id>[^/.]+)/fields",
    ProductTypeFieldViewSet,
    basename="producttype-field",
)

ProductTypesRouter.register("categories", CategoryViewSet, basename="category")
ProductTypesRouter.register(
    "categories/(?P<category_id>[^/.]+)/questions",
    CategoryQuestionViewSet,
    basename="category-question",
)
