import enum

from pydantic import BaseModel

from .menu import Menu
from .shopping_list import ShoppingList

__all__ = ["Week", "WeekOption"]


class WeekOption(str, enum.Enum):
    PREVIOUS = "previous"
    CURRENT = "current"


class Week(BaseModel):
    menu: Menu
    shopping_list: ShoppingList
