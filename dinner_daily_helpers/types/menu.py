import datetime as dt
import enum
from typing import List, Optional

from pydantic import BaseModel

__all__ = ["Menu"]


class ProteinCategory(int, enum.Enum):
    NONE = 0
    RED_MEAT = 1
    PORK = 2
    POULTRY = 3
    FISH = 4
    SHELLFISH = 5
    VEGETARIAN = 6


class DishType(int, enum.Enum):
    MAIN = 1
    SIDE = 2


class Option(BaseModel):
    id: int
    name: str


class Dish(BaseModel):
    big_image_url: Optional[str] = None
    cooking_time: float
    dish_type: DishType
    id: int
    ingredients: List[str]
    instructions: str
    is_personal: bool
    large_image_url: Optional[str] = None
    name: str
    preparation_time: float
    protein_category: Optional[ProteinCategory] = None
    small_image_url: Optional[str] = None


class DayMenu(BaseModel):
    calories: float
    carbs: float
    corner_note: str
    fat: float
    fiber: float
    id: int
    main: Optional[Dish] = None
    main_name: str
    main_recipe_options: List[Option]
    protein: float
    saturated_fat: float
    sides: List[Dish]
    sodium: float
    time_to_table: float


class MetaData(BaseModel):
    env: str
    family_size: int
    id: int
    is_new_user: bool


class Menu(BaseModel):
    id: int
    end_date: str
    start_date: str
    day_menus: List[DayMenu]
    is_original: bool
    metadata: MetaData
    name: str
    side_recipe_options: List[Option]

    @property
    def start_datetime(self):
        return dt.datetime.strptime(self.start_date, TIME_FORMAT)

    @property
    def end_datetime(self):
        return dt.datetime.strptime(self.end_date, TIME_FORMAT)
