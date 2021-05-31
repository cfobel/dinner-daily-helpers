import enum
from typing import List

from pydantic import BaseModel

__all__ = ["ShoppingList"]


class RecipeItem(BaseModel):
    recipe_id: int
    recipe_name: str
    shopping_list_item_id: int


class Item(BaseModel):
    brand: str
    cost: float
    dish_type: int
    formatted_amount: str
    id: int
    is_checked: bool
    is_fulfilled: bool
    is_on_sale: bool
    is_optional: bool
    name: str
    notes: str


class ShoppingList(BaseModel):
    dairy: List[Item]
    frozen_foods: List[Item]
    grocery: List[Item]
    meat_poultry: List[Item]
    produce: List[Item]
    seafood: List[Item]
    staples: List[Item]
    dairy_fulfilled: bool
    frozen_foods_fulfilled: bool
    grocery_fulfilled: bool
    meat_poultry_fulfilled: bool
    produce_fulfilled: bool
    seafood_fulfilled: bool
    staples_fulfilled: bool
    recipe_shop_items: List[RecipeItem]
    id: int
    name: str
    other: List[Item]
    cost_enabled: bool
