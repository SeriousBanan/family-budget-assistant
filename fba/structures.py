"""This module contains structures that used in the FBA."""

import dataclasses
import enum
from decimal import Decimal

from . import typedefs


class Priority(enum.IntEnum):
    """The priority of expenditure."""

    HIGHT = 0
    MEDIUM = enum.auto()
    LOW = enum.auto()


class ExpenditureType(enum.StrEnum):
    """The type of expenditure."""

    FOOD = enum.auto()
    HOUSE_RENT = enum.auto()
    UTILITY_BILLS = enum.auto()
    VACATION = enum.auto()
    ENTERTAINMENT = enum.auto()
    MOTHER_ASSIST = enum.auto()
    TRANSPORTATION = enum.auto()
    HOME_RENOVATION = enum.auto()
    BEAUTY = enum.auto()
    SAVINGS_AND_GIFTS = enum.auto()


@dataclasses.dataclass
class ExpenditureItem:
    priority: Priority
    type: ExpenditureType
    sharable: bool
    planned_budget: Decimal
    permanent: bool


@dataclasses.dataclass
class UserBudget:
    name: typedefs.UserName
    expenditures: list[ExpenditureItem]


@dataclasses.dataclass
class FamilyBudget:
    users_budgets: dict[typedefs.UserName, UserBudget]
