import enum
from copy import deepcopy
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import requests
from pydantic import BaseModel, Field, parse_raw_as

T = TypeVar("T")


class Query(BaseModel):
    key: str
    token: str


DEFAULT_QUERY = Query(key="<trello app key>", token="<trello api token>")


def init(query: Query):
    DEFAULT_QUERY.key = query.key
    DEFAULT_QUERY.token = query.token


NameField = Field(regex=r"^([0-9a-fA-F]{24}|\w+)$")
Objects = Dict[str, Any]


class PermissionLevel(str, enum.Enum):
    PRIVATE = "private"
    ORG = "org"
    BOARD = "board"


class Voting(str, enum.Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    MEMBERS = "members"


class CardAging(str, enum.Enum):
    PIRATE = "pirate"
    REGULAR = "regular"


class Prefs(BaseModel):
    permissionLevel: Optional[PermissionLevel]
    hideVotes: Optional[bool]
    voting: Optional[Voting]
    comments: Optional[str]
    invitations: Optional[Any]
    selfJoin: Optional[bool]
    cardCovers: Optional[bool]
    isTemplate: Optional[bool]
    cardAging: Optional[CardAging]
    calendarFeedEnabled: Optional[bool]
    background: Optional[str] = NameField
    backgroundImage: Optional[str]
    backgroundImageScaled: Optional[List[Objects]] = None


class Limits(BaseModel):
    attachments: Optional[Objects] = None


class Color(str, enum.Enum):
    BLACK = "black"
    BLUE = "blue"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    SKY = "sky"
    YELLOW = "yellow"
    lime = "lime"


class Label(BaseModel):
    id: Optional[str] = NameField
    idBoard: Optional[str] = NameField
    # The name displayed for the label.
    name: Optional[str] = None
    color: Optional[Color]


class CheckItemState(str, enum.Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


class Position(str, enum.Enum):
    TOP = "top"
    BOTTOM = "bottom"


class BoolStr(str, enum.Enum):
    TRUE = "true"
    FALSE = "false"


class BaseCheckItem(BaseModel):
    name: str


class NewCheckItem(BaseCheckItem):
    pos: Optional[Union[int, Position]] = None
    checked: Optional[BoolStr] = BoolStr.FALSE


class CheckItem(BaseCheckItem):
    due: Optional[str]
    id: str = NameField
    idChecklist: str = NameField
    idMember: Optional[str] = NameField
    nameData: Optional[Objects] = None
    pos: Union[int, Position]
    state: CheckItemState


class ChecklistId(BaseModel):
    id: Optional[str] = NameField


class BaseCheckList(BaseModel):
    name: str
    pos: Optional[Union[int, Position]] = None


class NewCheckList(BaseCheckList):
    idChecklistSource: Optional[str] = NameField


class CheckList(BaseModel):
    id: str = NameField
    idBoard: str = NameField
    idCard: str = NameField
    checkItems: List[CheckItem]

    def update_check_item(
        self,
        check_item: CheckItem,
        query: Optional[Dict[str, str]] = DEFAULT_QUERY,
    ):
        return update_check_item(self.idCard, check_item, query)


class BaseCard(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    pos: Union[int, Position] = None
    due: Optional[str] = None
    #     idList: str = NameField
    idList: Optional[str] = NameField
    idMembers: Optional[List[str]] = None
    idLabels: Optional[List[Union[Label, str]]] = None
    address: Optional[str] = None
    locationName: Optional[str] = None
    coordinates: Optional[str] = None


class NewCard(BaseCard):
    dueComplete: Optional[bool] = None
    # A URL starting with http:// or https:// or null
    urlSource: Optional[str] = None
    # A file
    fileSource: Optional[str] = None
    # The id of the card to copy into a new card.
    idCardSource: Optional[str] = NameField
    # Properties of the card to copy over from the source.
    keepFromSource: Optional[str] = None


class Card(BaseCard):
    id: Optional[str] = NameField
    badges: Optional[Objects] = None
    checkItemStates: Optional[List[str]] = None
    closed: Optional[bool] = None
    creationMethod: Optional[str] = None
    dateLastActivity: Optional[str] = None
    descData: Optional[Objects] = None
    dueReminder: Optional[str] = None
    email: Optional[str] = None
    idBoard: Optional[str] = NameField
    idChecklists: Optional[List[Union[Label, str]]] = None
    idMembersVoted: Optional[List[str]] = None
    idShort: Optional[int] = None
    idAttachmentCover: Optional[str] = None
    labels: Optional[List[Label]] = None
    limits: Optional[Limits] = None
    manualCoverAttachment: Optional[bool] = None
    shortLink: Optional[str] = None
    shortUrl: Optional[str] = None
    subscribed: Optional[bool] = None
    url: Optional[str] = None
    cover: Optional[Objects] = None

    @classmethod
    def get(
        cls: Type[T],
        id: NameField,
        fields: Optional[str] = "all",
        query: Optional[Dict[str, str]] = DEFAULT_QUERY,
    ) -> T:
        return get_card(id, fields, query)

    def get_checklists(
        self, query: Optional[Dict[str, str]] = DEFAULT_QUERY
    ) -> List[CheckList]:
        return get_checklists(self, query)


class Board(BaseModel):
    id: str = NameField
    name: str
    desc: Optional[str] = None
    descData: Optional[Objects] = None
    closed: Optional[bool] = False
    idMemberCreator: str = NameField
    idOrganization: str = NameField
    pinned: Optional[bool] = False
    url: Optional[str] = None
    shortUrl: Optional[str] = None
    prefs: Optional[Prefs] = None
    labelNames: Optional[Objects] = None
    limits: Optional[Limits] = None
    starred: Optional[bool] = False
    memberships: Optional[List[Objects]] = None
    shortLink: Optional[str] = False
    subscribed: Optional[bool] = False
    powerUps: Optional[List[str]] = None
    dateLastActivity: Optional[str] = None
    dateLastView: Optional[str] = None
    idTags: Optional[List[str]] = None
    datePluginDisable: Optional[str] = None
    creationMethod: Optional[str] = None
    ixUpdate: Optional[int] = None
    templateGallery: Optional[str] = None
    enterpriseOwned: Optional[bool] = None

    def get_cards(self, query: Optional[Dict[str, str]] = DEFAULT_QUERY) -> List[Card]:
        return get_cards(self, query)


def get_boards(
    member: str, query: Optional[Dict[str, str]] = DEFAULT_QUERY
) -> List[Board]:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-boards-get
    """
    url = f"https://api.trello.com/1/members/{ member }/boards"
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=query)
    return parse_raw_as(List[Board], response.text)


def get_cards(
    board: Union[str, Board], query: Optional[Dict[str, str]] = DEFAULT_QUERY
) -> List[Card]:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get
    """
    if isinstance(board, Board):
        board = board.id

    url = f"https://api.trello.com/1/boards/{ board }/cards"
    response = requests.request("GET", url, params=query)
    return parse_raw_as(List[Card], response.text)


def get_checklists(
    card: Union[str, Card], query: Optional[Dict[str, str]] = DEFAULT_QUERY
) -> List[CheckList]:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-id-checklists-get
    """
    if isinstance(card, Card):
        card = card.id
    url = f"https://api.trello.com/1/cards/{ card }/checklists"

    response = requests.request("GET", url, params=query)
    try:
        return parse_raw_as(List[CheckList], response.text)
    except Exception as exception:
        print(response.text)


def update_check_item(
    card: Union[str, Card],
    check_item: CheckItem,
    query: Optional[Dict[str, str]] = DEFAULT_QUERY,
):
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-idcard-checklist-idchecklist-checkitem-idcheckitem-put
    """
    if isinstance(card, Card):
        card = card.id

    url = f"https://api.trello.com/1/cards/{ card }/checkItem/{ check_item.id }"
    query = query.dict()
    query.update(**check_item.dict(exclude_none=True))

    response = requests.request("PUT", url, params=query)

    return CheckItem.parse_raw(response.text)


class List_(BaseModel):
    id: str = NameField
    name: str
    closed: Optional[bool] = None
    pos: Union[int, Position]
    softLimit: Optional[Any] = None
    idBoard: str = NameField
    subscribed: Optional[bool] = None


def get_lists(
    board: Union[str, Board], query: Optional[Dict[str, str]] = DEFAULT_QUERY
) -> List[List_]:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get
    """
    if isinstance(board, Board):
        board = board.id

    url = f"https://api.trello.com/1/boards/{ board }/lists"

    response = requests.request("GET", url, params=query)
    return parse_raw_as(List[List_], response.text)


def create_card(card: NewCard, query: Optional[Dict[str, str]] = DEFAULT_QUERY) -> Card:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-post
    """
    url = "https://api.trello.com/1/cards"
    query = query.dict()
    query.update(**card.dict(exclude_none=True))

    response = requests.request("POST", url, params=query)
    return Card.parse_raw(response.text)


def create_checklist(
    card: Union[str, Card],
    check_list: NewCheckList,
    query: Optional[Dict[str, str]] = DEFAULT_QUERY,
) -> CheckList:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-id-checklists-post
    """
    if isinstance(card, Card):
        card = card.id
    url = f"https://api.trello.com/1/cards/{ card }/checklists"
    query = query.dict()
    query.update(**check_list.dict(exclude_none=True))

    response = requests.request("POST", url, params=query)
    return CheckList.parse_raw(response.text)


def create_check_item(
    check_list: Union[str, CheckList],
    check_item: NewCheckItem,
    query: Optional[Dict[str, str]] = DEFAULT_QUERY,
) -> CheckItem:
    """
    https://developer.atlassian.com/cloud/trello/rest/api-group-checklists/#api-checklists-id-checkitems-post
    """
    if isinstance(check_list, CheckList):
        check_list = check_list.id
    url = f"https://api.trello.com/1/checklists/{ check_list }/checkItems"
    query = query.dict()
    query.update(**check_item.dict(exclude_none=True))

    response = requests.request("POST", url, params=query)
    try:
        return CheckItem.parse_raw(response.text)
    except:
        return response


def get_card(
    id: NameField,
    fields: Optional[str] = "all",
    query: Optional[Dict[str, str]] = DEFAULT_QUERY,
) -> Card:
    """
    Parameters
    ----------
    id
        ID of card to fetch.
    fields
        All or a comma-separated list of fields.

        Defaults: badges, checkItemStates, closed, dateLastActivity, desc, descData, due, email, idBoard, idChecklists, idLabels, idList, idMembers, idShort, idAttachmentCover, manualCoverAttachment, labels, name, pos, shortUrl, url
    query

    See https://developer.atlassian.com/cloud/trello/rest/api-group-checklists/#api-checklists-id-checkitems-post
    """
    query = query.dict()
    query.update(fields=fields)

    url = f"https://api.trello.com/1/cards/{ id }"
    response = requests.request("GET", url, params=query)
    return Card.parse_raw(response.text)
