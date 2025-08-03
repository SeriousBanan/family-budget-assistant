from decimal import Decimal
from pathlib import Path

import yaml

from fba import structures


def load_from_file(budget_file_path: Path) -> structures.FamilyBudget:
    with budget_file_path.open("r", encoding="utf-8") as budget_file:
        budget_data = yaml.safe_load(budget_file)

    budget = structures.FamilyBudget(users_budgets={})

    for user in budget_data["users_budgets"].values():
        budget.users_budgets[user["name"]] = structures.UserBudget(
            name=user["name"], expenditures=[]
        )

        for expenditure in user["expenditures"]:
            budget.users_budgets[user["name"]].expenditures.append(
                structures.ExpenditureItem(
                    structures.Priority(expenditure["priority"]),
                    structures.ExpenditureType(expenditure["type"]),
                    expenditure["sharable"],
                    Decimal(expenditure["planned_budget"]),
                    expenditure["permanent"],
                )
            )

    return budget
