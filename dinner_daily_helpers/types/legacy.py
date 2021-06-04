import datetime as dt
import re
from typing import List, Optional, TypeVar

import pint
from pydantic import BaseModel

from .menu import TIME_FORMAT, DayMenu
from .menu import Dish as Dish_
from .menu import DishType, Menu, MetaData, ProteinCategory

__all__ = [
    "LegacyMenu",
    "from_legacy",
    "to_legacy",
]

T = TypeVar("T")

ureg = pint.get_application_registry()

CRE_FAMILY_SIZE = re.compile(r"(?P<family_size>\d+)$")
CRE_DATE = re.compile(f"^(?P<month>\w+)\s+(?P<day>\d+)(st|nd|rd|th)?\s+(?P<year>\d+)$")
LEGACY_MAP = {"Cals": "calories"}
for k in ("Protein", "Fat", "Fiber", "Carbs"):
    LEGACY_MAP[k] = k.lower()
NEW_TO_LEGACY_MAP = {v: k for k, v in LEGACY_MAP.items()}


class Dish(BaseModel):
    title: str
    ingredients: List[str]
    instructions: List[str]


class Meal(BaseModel):
    duration: str
    notes: Optional[List[str]] = None
    main_dish: Dish
    nutrition: List[str]
    side_dishes: List[Dish]


class LegacyMenu(BaseModel):
    date: str
    meals: List[Meal]
    servings: str
    store: str
    title: str


class Nutrition(BaseModel):
    calories: float
    carbs: float
    fat: float
    fiber: float
    protein: float
    saturated_fat: float
    sodium: float

    @classmethod
    def from_list(cls, nutrition: List[str]) -> "Nutrition":

        CRE_QUANTITY = re.compile(
            r"^(?P<quantity>\d+(\.(\d+))?)\D*\s+(?P<nutrient>.*)$"
        )
        legacy_matches = {
            nutrient_quantity: CRE_QUANTITY.match(nutrient_quantity)
            for nutrient_quantity in nutrition
        }
        legacy_mapped = {
            LEGACY_MAP[match.group("nutrient")]: float(match.group("quantity"))
            for nutrient_quantity, match in legacy_matches.items()
        }
        return cls(saturated_fat=0, sodium=0, **legacy_mapped)


def from_legacy(menu: LegacyMenu) -> Menu:
    day_menus = [
        DayMenu(
            corner_note=" ".join(meal.notes) if meal.notes is not None else "",
            id=0,
            main=Dish_(
                cooking_time=0,
                preparation_time=0,
                dish_type=DishType.MAIN,
                id=0,
                ingredients=meal.main_dish.ingredients,
                instructions="  ".join(meal.main_dish.instructions),
                is_personal=False,
                name=meal.main_dish.title,
                protein_category=ProteinCategory.NONE,
            ),
            main_name=meal.main_dish.title,
            main_recipe_options=[],
            sides=[
                Dish_(
                    cooking_time=0,
                    preparation_time=0,
                    dish_type=DishType.SIDE,
                    id=0,
                    ingredients=dish.ingredients,
                    instructions=" ".join(dish.instructions),
                    is_personal=False,
                    name=dish.title,
                    protein_category=ProteinCategory.NONE,
                )
                for dish in meal.side_dishes
            ],
            time_to_table=ureg.parse_expression(meal.duration).to("minute").magnitude,
            **Nutrition.from_list(meal.nutrition).dict(),
        )
        for meal in menu.meals
    ]
    metadata = MetaData(
        env=menu.store,
        family_size=int(CRE_FAMILY_SIZE.search(menu.servings).group("family_size")),
        id=0,
        is_new_user=False,
    )

    start_date_str = "{month} {day} {year}".format(
        **CRE_DATE.match(menu.date).groupdict()
    )
    start_date = dt.datetime.strptime(start_date_str, "%B %d %Y")
    return Menu(
        id=0,
        start_date=start_date.strftime(TIME_FORMAT),
        end_date=(start_date + dt.timedelta(days=7)).strftime(TIME_FORMAT),
        day_menus=day_menus,
        is_original=True,
        metadata=metadata,
        name=menu.title,
        side_recipe_options=[],
    )


def split_sentences(paragraph: str) -> List[str]:
    return re.sub(r"([\.!])+\s+", "\g<1>\n", paragraph).splitlines()


def ord(n):
    return str(n) + (
        "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )


def dt_stylish(dt, f):
    return dt.strftime(f).replace("{th}", ord(dt.day))


def to_legacy(menu: Menu) -> LegacyMenu:
    start_date = dt.datetime.strptime(menu.start_date, TIME_FORMAT)
    return LegacyMenu(
        date=dt_stylish(start_date, "%B {th} %Y"),
        meals=[
            Meal(
                duration=f"{ int(day_menu.time_to_table) } mins"
                if day_menu.time_to_table < 120
                else f"{ int(day_menu.time_to_table / 60) } hrs",
                notes=split_sentences(day_menu.corner_note)
                if day_menu.corner_note
                else None,
                main_dish=Dish(
                    title=day_menu.main.name,
                    ingredients=day_menu.main.ingredients,
                    # instructions=re.split(r"\s{2,}", day_menu.main.instructions),
                    instructions=split_sentences(day_menu.main.instructions),
                ),
                nutrition=[
                    f"{ int(getattr(day_menu, nutrient)) }{ 'g' if legacy_nutrient not in ('Cals', ) else '' } { legacy_nutrient }"
                    for nutrient, legacy_nutrient in NEW_TO_LEGACY_MAP.items()
                ],
                side_dishes=[
                    Dish(
                        title=dish.name,
                        ingredients=dish.ingredients,
                        # instructions=re.split(r"\s{2,}", dish.instructions),
                        instructions=split_sentences(dish.instructions),
                    )
                    for dish in day_menu.sides
                ],
            )
            for day_menu in menu.day_menus
        ],
        servings=f"Serves { menu.metadata.family_size - 1 } to { menu.metadata.family_size }",
        store=menu.metadata.env,
        title=menu.name,
    )
