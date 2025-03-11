from .bestand import BestandAdmin
from .content import ContentLabelAdmin
from .jsonschema import JsonSchemaAdmin
from .link import LinkAdmin
from .prijs import PrijsAdmin
from .producttype import ProductTypeAdmin
from .thema import ThemaAdmin
from .upn import UniformeProductNaamAdmin

__all__ = [
    "ProductTypeAdmin",
    "BestandAdmin",
    "LinkAdmin",
    "UniformeProductNaamAdmin",
    "PrijsAdmin",
    "ThemaAdmin",
    "ContentLabelAdmin",
    "JsonSchemaAdmin",
]
