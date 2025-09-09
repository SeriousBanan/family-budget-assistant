import dataclasses
import decimal
import typing
from collections import defaultdict
from pathlib import Path

from fba.sotrage_processors import yaml_file_storage
from fba.structures import ExpenditureItem
from fba.typedefs import UserName


@dataclasses.dataclass
class ExpenditureAnalyzeInfo:
    user_name: str
    expenditure: ExpenditureItem
    remaining_funds: decimal.Decimal


def round_income(income: decimal.Decimal) -> decimal.Decimal:
    return income.quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_CEILING)


def input_decimal(prompt: str) -> decimal.Decimal:
    while True:
        try:
            value = decimal.Decimal(input(prompt))
            return value
        except decimal.DecimalException:
            print("Wrong input. Try again.")


def main() -> None:
    budget_file_path: typing.Final = Path("budget.yaml")

    budget = yaml_file_storage.load_from_file(budget_file_path)

    expenditures_by_users: defaultdict[UserName, list[ExpenditureAnalyzeInfo]] = (
        defaultdict(list)
    )
    sharable_expenditures_by_type: defaultdict[
        UserName, list[ExpenditureAnalyzeInfo]
    ] = defaultdict(list)

    for user_name, user_budget in budget.users_budgets.items():
        for expenditure in user_budget.expenditures:
            info = ExpenditureAnalyzeInfo(user_name, expenditure, decimal.Decimal(0))
            if expenditure.sharable:
                sharable_expenditures_by_type[expenditure.type].append(info)
            else:
                expenditures_by_users[user_name].append(info)

    _request_remaining_funds_sharable(sharable_expenditures_by_type)
    _request_remaining_funds_personal(expenditures_by_users)

    for expenditures_infos in sharable_expenditures_by_type.values():
        for info in expenditures_infos:
            expenditures_by_users[info.user_name].append(info)

    users_incomes = _request_users_incomes(budget.users_budgets.keys())

    print()

    _analyze_user_budget(expenditures_by_users, users_incomes)


def _request_remaining_funds_sharable(
    sharable_expenditures_by_type: dict[UserName, list[ExpenditureAnalyzeInfo]],
) -> None:
    print("Request for remaining funds of sharable expenditures")

    for expenditure_type, expenditures_infos in sharable_expenditures_by_type.items():
        if expenditures_infos[0].expenditure.permanent:
            continue
        remaining_funds = input_decimal(f"\t{expenditure_type}? ")
        total_planned_budget = sum(
            (info.expenditure.planned_budget for info in expenditures_infos),
            start=decimal.Decimal(0),
        )
        for info in expenditures_infos:
            planned_budget_ratio = (
                info.expenditure.planned_budget / total_planned_budget
            )
            info.remaining_funds = remaining_funds * planned_budget_ratio


def _request_remaining_funds_personal(
    expenditures_by_users: dict[UserName, list[ExpenditureAnalyzeInfo]],
) -> None:
    for user_name, expenditures_infos in expenditures_by_users.items():
        print(f"Requesting {user_name} for remaining funds of expenditures")
        for info in expenditures_infos:
            if info.expenditure.permanent:
                continue
            remaining_funds = input_decimal(f"\t{info.expenditure.type}? ")

            info.remaining_funds = remaining_funds


def _request_users_incomes(
    users: typing.Iterable[UserName],
) -> dict[UserName, decimal.Decimal]:
    users_incomes: dict[UserName, decimal.Decimal] = {}
    print("Requesting Users incomes")

    for user_name in users:
        income = input_decimal(f"\t{user_name}? ")

        users_incomes[user_name] = income

    return users_incomes


def _analyze_user_budget(
    expenditures_by_users: dict[UserName, list[ExpenditureAnalyzeInfo]],
    users_incomes: dict[UserName, decimal.Decimal],
) -> None:
    for user_name, expenditures_infos in expenditures_by_users.items():
        expenditures_infos.sort(key=lambda info: info.expenditure.priority)

        print(f"Analyze for {user_name} income:")
        user_income = users_incomes[user_name]

        for expenditure_info in expenditures_infos:
            expenditure_refill = min(
                expenditure_info.expenditure.planned_budget
                - expenditure_info.remaining_funds,
                user_income,
            )

            user_income -= expenditure_refill

            print(
                f"\t{expenditure_info.expenditure.type}: {round_income(expenditure_refill)}"
            )

        print(f"\tLeft income: {round_income(user_income)}")


if __name__ == "__main__":
    import sys

    try:
        main()

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
