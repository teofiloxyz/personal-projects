import re
from enum import Enum
from typing import Optional

from database import Edit
from fintracker import Fintracker, Report
from utils import Utils, Date

# Balance.edit method and related methods still need refactoring and testing


class Category(Enum):
    ASSETS = "Assets"
    LIABILITIES = "Liabilities"


class AssetsLiabilities:
    def __init__(self) -> None:
        self.utils = Utils()
        self.report = Report()
        self.items: dict
        self.category: str

    def get_total(self) -> int:
        return sum(self.items.values())

    def get_items(self) -> dict:
        return self.items

    def get_items_as_currency(self) -> list[tuple[str, str]]:
        return [
            (item.capitalize(), self.utils.as_currency(amount))
            for item, amount in self.items.items()
        ]

    def get_item_val(self, item: str) -> float:
        if item in self.items.keys():
            return self.items[item]
        return 0

    def check_for_negative_items(self) -> None:
        [
            self.report.show_negative_item(item, val)
            for item, val in self.items.items()
            if val < 0
        ]

    def create_new_item(self) -> Optional[str]:
        while True:
            item = (
                input(f"Enter name for the new {self.category}: ")
                .lower()
                .strip()
            )
            if item == "q":
                return None
            elif item in self.items.keys() or item == "create new":
                print(f"Cannot create {self.category}: '{item}'")
                continue
            self.items[item] = 0
            return item

    def update_item_value(self, item: str, value: float) -> None:
        self.items[item] = value

    def eliminate_null_items(self) -> None:
        items_to_delete = [item for item, val in self.items.items() if val == 0]
        [self.delete_item(item) for item in items_to_delete]

    def delete_item(self, item: str) -> None:
        del self.items[item]


class Assets(AssetsLiabilities):
    def __init__(self) -> None:
        super().__init__()
        self.items = Fintracker().balance[Category.ASSETS.value]
        self.category = "asset"

    def change_cash_amount(self, amount: float) -> None:
        self._check_cash_item()
        self.items["cash"] += amount
        Balance().save_items()

    def _check_cash_item(self) -> None:
        if "cash" not in self.items.keys():
            self.items["cash"] = 0


class Liabilities(AssetsLiabilities):
    def __init__(self) -> None:
        super().__init__()
        self.items = Fintracker().balance[Category.LIABILITIES.value]
        self.category = "liability"


class Balance:
    assets, liabilities = Assets(), Liabilities()  # Ñ usar __init__
    fintracker, report = Fintracker(), Report()
    utils, date = Utils(), Date()

    def show(self) -> None:
        assets = self.assets.get_items_as_currency()
        liabilities = self.liabilities.get_items_as_currency()
        assets_total = self.assets.get_total()
        liabilities_total = self.liabilities.get_total()

        assets.append(("Total Assets", self.utils.as_currency(assets_total)))
        liabilities.append(
            ("Total Liabilities", self.utils.as_currency(liabilities_total))
        )

        balance = assets + liabilities
        balance_total = assets_total - liabilities_total
        balance.append(("Balance", self.utils.as_currency(balance_total)))

        self.report.show_balance(balance)

    def edit(self) -> None:
        balance_items = self._get_copy_of_balance_items()
        first_item_info = self._pick_first_item(balance_items)
        if not first_item_info:
            print("Aborting...")
            return
        first_item_category, first_item, first_item_value = first_item_info

        first_item_amount_diff = self._get_first_item_new_val(
            first_item, first_item_value
        )
        if not first_item_amount_diff:
            print("Aborting...")
            return

        """ Show again all balance items except the chosen """
        if first_item in balance_items[first_item_category].keys():
            del balance_items[first_item_category][first_item]
        balance_operation = self._get_operation(
            first_item_category, first_item_amount_diff
        )
        second_item_info = self._pick_second_item(
            balance_items, balance_operation
        )
        if not second_item_info:
            print("Aborting...")
            return
        second_item_category, second_item, second_item_value = second_item_info

        """ If not isolated balance operation """
        if second_item:
            second_item_gets_negative = (
                self._check_if_second_item_gets_negative(
                    first_item_category,
                    first_item_amount_diff,
                    second_item_category,
                    second_item_value,
                )
            )
            if second_item_gets_negative:
                first_item_amount_diff = self._get_max_amount_from_second_item(
                    first_item_info,
                    second_item_info,
                )
                if not first_item_amount_diff:
                    print("Aborting...")
                    return

        if first_item_category == Category.ASSETS:
            self.assets.update_item_value(
                first_item, first_item_value + first_item_amount_diff
            )
        else:
            self.liabilities.update_item_value(
                first_item, first_item_value + first_item_amount_diff
            )
        """ If not isolated balance operation """
        if second_item:
            if first_item_category == second_item_category:
                second_item_amount_diff = -first_item_amount_diff
            else:
                second_item_amount_diff = first_item_amount_diff
            if second_item_category == Category.ASSETS:
                self.assets.update_item_value(
                    second_item, second_item_value + second_item_amount_diff
                )
            else:
                self.liabilities.update_item_value(
                    second_item, second_item_value + second_item_amount_diff
                )

        now = self.date.get_now(date_format="%Y-%m-%d %H:%M:%S")
        description = self._create_operation_description(
            first_item_category,
            first_item,
            second_item_category,
            second_item,
            first_item_amount_diff,
        )
        entry = now, "Balance", abs(first_item_amount_diff), description
        Edit().add_transaction(entry)

        self.save_items()

    def _get_copy_of_balance_items(self) -> dict:
        return {
            Category.ASSETS: dict(self.assets.get_items()),
            Category.LIABILITIES: dict(self.liabilities.get_items()),
        }

    def _pick_first_item(self, balance_items: dict) -> Optional[tuple]:
        return self._pick_item(
            balance_items,
            question="Choose the item to edit: ",
            is_first_item=True,
        )

    def _pick_item(
        self, balance_items: dict, question: str, is_first_item: bool
    ) -> Optional[tuple]:
        while True:
            items, n = list(), 1
            print("\nAssets:")
            print(f"[{n}] Create new asset")
            items.append((Category.ASSETS, "create new", 0))
            for n, asset in enumerate(
                balance_items[Category.ASSETS].keys(), n + 1
            ):
                print(f"[{n}] {asset.capitalize()}")
                items.append(
                    (Category.ASSETS, asset, self.assets.get_item_val(asset))
                )

            print("\nLiabilities:")
            print(f"[{n + 1}] Create new liability")
            items.append((Category.LIABILITIES, "create new", 0))
            for n, liability in enumerate(
                balance_items[Category.LIABILITIES].keys(), n + 2
            ):
                print(f"[{n}] {liability.capitalize()}")
                items.append(
                    (
                        Category.LIABILITIES,
                        liability,
                        self.liabilities.get_item_val(liability),
                    )
                )

            prompt = input(f"\n{question}")
            if prompt in ("q", "0"):
                return None
            elif prompt == "" and not is_first_item:
                return None, None, None
            try:
                item_info = items[int(prompt) - 1]
                if item_info[1] == "create new":
                    item_info = self._create_new_item(item_info)
                    if not item_info:
                        return None
                return item_info
            except (ValueError, IndexError):
                print("Pick a number within those...")
                continue

    def _create_new_item(self, item_info: tuple) -> Optional[tuple]:
        if item_info[0] == Category.ASSETS:
            item = self.assets.create_new_item()
        else:
            item = self.liabilities.create_new_item()
        if not item:
            return None
        return (item_info[0], item, item_info[2])

    def _get_first_item_new_val(
        self, item: str, current_val: float
    ) -> Optional[float]:
        print(
            f"Current value of {item.capitalize()}: "
            f"{self.utils.as_currency(current_val)}"
        )
        while True:
            new_val = input(f"Enter the new value for {item.capitalize()}: ")
            if new_val == "q":
                return None
            try:
                new_val = float(new_val)
            except ValueError:
                print("Must be a number...")
                continue
            if new_val < 0:
                print("Cannot be negative!")
                continue
            return round(new_val - current_val, 2)

    def _get_operation(
        self, category: Category, amount: float
    ) -> dict[str, str]:
        amount_abs = self.utils.as_currency(abs(amount))

        if (amount > 0 and category == Category.ASSETS) or (
            amount < 0 and category == Category.LIABILITIES
        ):
            return {
                "asset": f"subtract {amount_abs}",
                "liability": f"add {amount_abs}",
            }
        else:
            return {
                "asset": f"add {amount_abs}",
                "liability": f"subtract {amount_abs}",
            }

    def _pick_second_item(
        self, balance_items: dict, balance_operation: dict
    ) -> Optional[tuple]:
        question = (
            f"Choose an asset to {balance_operation['asset']} or liability "
            f"to {balance_operation['liability']}, or leave empty if the "
            "operation is isolated: "
        )
        return self._pick_item(balance_items, question, is_first_item=False)

    def _check_if_second_item_gets_negative(
        self,
        first_item_category: Category,
        first_item_amount_diff: float,
        second_item_category: Category,
        second_item_value: float,
    ) -> bool:
        if first_item_category == second_item_category:
            second_item_amount_diff = -first_item_amount_diff
        else:
            second_item_amount_diff = first_item_amount_diff

        if second_item_value + second_item_amount_diff < 0:
            return True
        return False

    def _get_max_amount_from_second_item(
        self,
        first_item_info: tuple,
        second_item_info: tuple,
    ) -> Optional[float]:
        print(f"{second_item_info[1].capitalize()}, cannot become negative...")
        if first_item_info[0] == second_item_info[0]:
            new_first_item_value = first_item_info[2] + second_item_info[2]
        else:
            new_first_item_value = first_item_info[2] - second_item_info[2]
        question = (
            f"Change {first_item_info[1].capitalize()} value to "
            f"{self.utils.as_currency(new_first_item_value)} instead, "
            f"to use all the amount of {second_item_info[1].capitalize()} [y/N]? "
        )
        if input(question) in ("y", "Y"):
            return new_first_item_value - first_item_info[2]
        return None

    def _create_operation_description(
        self,
        first_item_category: Category,
        first_item: str,
        second_item_category: Category | None,
        second_item: str | None,
        amount: float,
    ) -> str:
        first_item_opr = "-" if amount < 0 else "+"
        description = (
            f"{first_item_opr}{first_item_category.value[0]}:{first_item}"
        )
        if not second_item_category:  # If is isolated balance operation
            return description

        if first_item_category == second_item_category:
            second_item_opr = "+" if amount < 0 else "-"
        else:
            second_item_opr = "-" if amount < 0 else "+"

        description += (
            f" {second_item_opr}{second_item_category.value[0]}:{second_item}"
        )
        return description

    def change_cash_amount(self, amount: float) -> None:
        return self.assets.change_cash_amount(amount)

    def revert_items_amount(self, note: str, amount: float) -> None:
        """In case a balance transaction/operation is removed/voided"""

        first_item_note = re.sub(" [-+][LA]:.*$", "", note)
        first_item_amount_diff = self._get_item_amount_diff(
            first_item_note, amount
        )
        first_item_category = self._get_category_from_note(first_item_note)
        first_item = first_item_note[3:]
        self._change_item_value(
            first_item_category, first_item, first_item_amount_diff
        )

        second_item_note = note.replace(first_item_note, "").strip()
        if second_item_note == "":
            self.save_items()
            return
        """If it wasn't an isolated balance transaction,
        reverse the amount of the second item"""
        second_item_amount_diff = self._get_item_amount_diff(
            second_item_note, amount
        )
        second_item_category = self._get_category_from_note(second_item_note)
        second_item = second_item_note[3:]
        self._change_item_value(
            second_item_category, second_item, second_item_amount_diff
        )
        self.save_items()

    def _get_category_from_note(self, item_note: str) -> Category:
        if item_note[1] == Category.ASSETS.value[0]:
            return Category.ASSETS
        return Category.LIABILITIES

    def _get_item_amount_diff(self, item_note: str, amount: float) -> float:
        if item_note[0] == "+":
            return -amount
        return amount

    def _change_item_value(
        self, category: Category, item: str, amount: float
    ) -> None:
        if category == Category.ASSETS:
            item_val = self.assets.get_item_val(item)
            self.assets.update_item_value(item, item_val + amount)
        else:
            item_val = self.liabilities.get_item_val(item)
            self.liabilities.update_item_value(item, item_val + amount)

    def save_items(self) -> None:
        self.assets.eliminate_null_items()
        self.liabilities.eliminate_null_items()
        self.assets.check_for_negative_items()
        self.liabilities.check_for_negative_items()
        balance = {
            Category.ASSETS.value: self.assets.get_items(),
            Category.LIABILITIES.value: self.liabilities.get_items(),
        }
        self.fintracker.save_balance(balance)
