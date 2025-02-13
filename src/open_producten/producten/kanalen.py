from notifications_api_common.kanalen import Kanaal

from .models import Product

KANAAL_PRODUCTEN = Kanaal(
    "producten", main_resource=Product, kenmerken=("product_type_id",)
)
