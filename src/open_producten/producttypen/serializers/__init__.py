from .bestand import BestandSerializer
from .link import LinkSerializer
from .onderwerp import OnderwerpSerializer
from .prijs import PrijsOptieSerializer, PrijsSerializer
from .producttype import ProductTypeActuelePrijsSerializer, ProductTypeSerializer
from .vraag import VraagSerializer

__all__ = [
    "LinkSerializer",
    "BestandSerializer",
    "OnderwerpSerializer",
    "PrijsSerializer",
    "PrijsOptieSerializer",
    "ProductTypeSerializer",
    "ProductTypeActuelePrijsSerializer",
    "VraagSerializer",
]
