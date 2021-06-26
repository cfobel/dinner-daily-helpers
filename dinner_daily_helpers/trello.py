import enum
from typing import Dict, Optional, TypeVar, Union

from .trello_api import (
    DEFAULT_QUERY,
    Card,
    List_,
    NewCard,
    NewCheckItem,
    NewCheckList,
    Position,
    create_card,
    create_check_item,
    create_checklist,
)
from .types.week import Week

T = TypeVar("T")


class StoreSection(str, enum.Enum):
    PRODUCE = "produce"
    GROCERY = "grocery"
    STAPLES = "staples"
    MEAT_POULTRY = "meat_poultry"
    SEAFOOD = "seafood"
    FROZEN_FOODS = "frozen_foods"
    OTHER = "other"
    DAIRY = "dairy"


def create_week_card(
    week: Week,
    list_: Union[str, List_],
    pos: Union[int, Position] = Position.TOP,
    query: Optional[Dict[str, str]] = DEFAULT_QUERY,
) -> Card:
    """
    Add a ``Card`` to the specified Trello ``List`` with ``CheckList`` for each grocery category.
    """
    start_date = week.menu.start_datetime.strftime("%Y-%m-%d")
    description = "\n".join(
        [
            f"- { day_menu.main.name } _({ int(day_menu.calories) } calories, "
            f"**{ int(sum((day_menu.main.preparation_time, day_menu.main.cooking_time))) }"
            f"min** = { int(day_menu.main.preparation_time) } min prep "
            f"+ { int(day_menu.main.cooking_time) } min cooking)_"
            for day_menu in week.menu.day_menus
            if day_menu.main
        ]
    )
    new_card = NewCard(
        name=f"{ week.menu.name } ({ start_date })",
        desc=f"https://dinner-daily-scraper-bzc2fa4mva-ue.a.run.app/menu/?start_date={ start_date }\n\n{ description }",
        pos=pos,
        idList=list_.id if isinstance(list_, List_) else list_,
    )
    card = create_card(new_card, query=query)

    for store_section in StoreSection:
        # Create a checklist.
        new_check_list = NewCheckList(name=store_section, pos=Position.BOTTOM)
        check_list = create_checklist(card, new_check_list, query=query)

        for item in getattr(week.shopping_list, store_section):
            # Add item to checklist
            new_check_item = NewCheckItem(
                name=f"{ item.name } ({ item.formatted_amount })",
                pos=Position.BOTTOM,
                checked=str(item.is_checked).lower(),
            )
            check_item = create_check_item(
                check_list=check_list, check_item=new_check_item, query=query
            )
    return card
