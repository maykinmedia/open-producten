from open_producten.utils.kanaal import Kanaal

from .models import Product

KANAAL_PRODUCTEN = Kanaal(
    "producten",
    main_resource=Product,
    kenmerken=("product_type.id",),  # TODO decide on kenmerken
)
