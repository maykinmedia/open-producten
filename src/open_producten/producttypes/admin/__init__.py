from .category import CategoryAdmin
from .condition import ConditionAdmin
from .file import FileAdmin
from .link import LinkAdmin
from .price import PriceAdmin
from .producttype import ProductTypeAdmin
from .question import QuestionAdmin
from .tag import TagAdmin
from .upn import UniformProductNameAdmin

__all__ = [
    "ProductTypeAdmin",
    "ConditionAdmin",
    "FileAdmin",
    "LinkAdmin",
    "QuestionAdmin",
    "TagAdmin",
    "UniformProductNameAdmin",
    "PriceAdmin",
    "CategoryAdmin",
]
