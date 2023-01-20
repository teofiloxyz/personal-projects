import re
from enum import Enum
from typing import Optional

from fintracker import Fintracker, Report
from database import Edit
from utils import Utils, Date


class Category(Enum):
    ASSETS = "Assets"
    LIABILITIES = "Liabilities"


class AssetsLiabilities:
    def __init__(self) -> None:
        self.utils = Utils()
        self.items = dict()
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

    def create_new_item(self) -> Optional[str]:
        while True:
            item = input(f"Enter name for the new {self.category}: ").lower()
            if item == "q":
                return None
            elif item in self.items.keys() or item == "create new":
                print(f"Cannot create {self.category}: '{item}'")
                continue
            self.items[item] = 0
            return item

    def update_item_value(self, item: str, value: float) -> None:
        self.items[item] = value

    def delete_item(self, item: str) -> None:
        del self.items[item]


class Assets(AssetsLiabilities):
    def __init__(self) -> None:
        self.items = Fintracker().balance["assets"]
        self.category = "asset"
        self._check_cash_item()

    def change_cash_amount(self, amount: float) -> None:
        self.items["cash"] += amount

    def _check_cash_item(self) -> None:
        if "cash" not in self.items.keys():
            self.items["cash"] = 0


class Liabilities(AssetsLiabilities):
    def __init__(self) -> None:
        self.items = Fintracker().balance["liabilities"]
        self.category = "liability"


class Balance:
    fintracker, report = Fintracker(), Report()
    assets, liabilities = Assets(), Liabilities()
    utils, date = Utils(), Date()

    def __exit__(self) -> None:
        self.fintracker.save()
        self._check_for_negative_items()

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
        balance_items = self._get_balance_items()
        first_item_info = self._pick_first_item(balance_items)
        if not first_item_info:
            print("Aborting...")
            return
        first_item_category, first_item, first_item_value = first_item_info

        amount = self._get_item_new_val(first_item, first_item_value)
        if not amount:
            print("Aborting...")
            return

        """ Show again all balance items except the chosen """
        del balance_items[first_item_category.value][first_item]
        balance_operation = self._get_operation(first_item_category, amount)
        second_item_info = self._pick_second_item(
            balance_items, balance_operation
        )
        if not second_item_info:
            print("Aborting...")
            return
        second_item_category, second_item, second_item_value = second_item_info

        if first_item_category == Category.ASSETS:
            self.assets.update_item_value(first_item, first_item_value + amount)
        else:
            self.liabilities.update_item_value(
                first_item, first_item_value + amount
            )
        """ If item not isolated operation """
        if second_item:
            if first_item_category == second_item_category:
                amount = -amount
            if first_item_category == Category.ASSETS:
                self.assets.update_item_value(
                    second_item, second_item_value + amount
                )
            else:
                self.liabilities.update_item_value(
                    second_item, second_item_value + amount
                )

        now = self.date.get_now(date_format="%Y-%m-%d %H:%M:%S")
        description = self._create_operation_description(
            first_item_category,
            first_item,
            second_item_category,
            second_item,
            amount,
        )
        entry = now, "Balance", abs(amount), description
        Edit().add_transaction(entry)

    def _pick_first_item(self, balance: tuple[dict, dict]) -> Optional[tuple]:
        return self._pick_item(
            balance, prompt="Choose the item to edit: ", is_first_item=True
        )

    def _pick_item(
        self, balance_items: tuple[dict, dict], prompt: str, is_first_item: bool
    ) -> Optional[tuple]:
        while True:
            items, n = list(), 1
            print("\nAssets:")
            print(f"[{n}] Create new asset")
            items.append(("assets", "create new"))
            for n, asset in enumerate(balance_items[0].keys(), n + 1):
                print(f"[{n}] {asset.capitalize()}")
                items.append(("assets", asset))

            print("\nLiabilities:")
            print(f"[{n + 1}] Create new liability")
            items.append(("liabilities", "create new"))
            for n, liability in enumerate(balance_items[1].keys(), n + 2):
                print(f"[{n}] {liability.capitalize()}")
                items.append(("liabilities", liability))

            prompt = input("\n")
            if prompt == "q":
                return None
            elif prompt == "" and not is_first_item:
                return None, None, None
            try:
                return items[int(prompt) - 1]
            except (ValueError, IndexError):
                print("Pick a number within those...")
                continue

    def _create_new_item(self, category: Category) -> Optional[str]:
        if category == Category.ASSETS:
            return self.assets.create_new_item()
        return self.liabilities.create_new_item()

    def _get_item_new_val(
        self, item: str, current_val: float
    ) -> Optional[float]:
        print(f"Current value of {item.capitalize()}: {current_val}")
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
        self, balance_items: tuple[dict, dict], balance_operation: dict
    ) -> Optional[tuple]:
        question = (
            f"Choose an asset to {balance_operation['asset']} or liability "
            f"to {balance_operation['liability']}, or leave empty if is "
            "isolated: "
        )
        self._pick_item(balance_items, prompt=question, is_first_item=False)

    def _create_operation_description(
        self,
        first_item_category: Category,
        first_item: str,
        second_item_category: Category,
        second_item: str,
        val_diff: float,
    ) -> str:
        item_1_opr = "-" if val_diff < 0 else "+"
        description = f"{item_1_opr}{first_item_category.value[0]}:{first_item}"
        if first_item_category == second_item_category:
            item_2_opr = "+" if val_diff < 0 else "-"
        else:
            item_2_opr = "-" if val_diff < 0 else "+"

        if second_item_category != "":  # In case of isolated
            description += (
                f" {item_2_opr}{second_item_category.value[0]}:{second_item}"
            )
        return description

    def _check_for_negative_items(self) -> None:
        negative_items = self._get_negative_items()
        if len(negative_items) > 0:
            self.report.show_balance_negative_items(negative_items)

    def _get_balance_items(self) -> tuple[dict, dict]:
        return self.assets.get_items(), self.liabilities.get_items()

    def _get_negative_items(self) -> list[str]:
        return [
            item
            for category in self._get_balance_items()
            for item, amount in category.items()
            if amount < 0
        ]

    def change_cash_amount(self, amount: float) -> None:
        return self.assets.change_cash_amount(amount)

    def revert_items_amount(self, note: str, amount: float) -> None:
        """In case a balance transaction is removed/voided"""

        item_1_note = re.sub(" [-+][la]:.*$", "", note)
        if item_1_note[0] == "-":
            amount = -amount
        first_item_category = self._get_category_from_note(item_1_note)
        first_item = item_1_note[3:]
        self._change_item_amount(first_item_category, first_item, amount)

        item_2_note = note.replace(item_1_note, "").strip()
        if item_2_note == "":
            return
        """If it wasn't an isolated balance transaction,
        reverse the amount of the second item"""
        if item_2_note[0] == "-":
            amount = -amount
        second_item_category = self._get_category_from_note(item_2_note)
        second_item = item_2_note[3:]
        self._change_item_amount(second_item_category, second_item, amount)

    def _get_category_from_note(self, item_note: str) -> Category:
        if item_note[1] == "a":
            return Category.ASSETS
        return Category.LIABILITIES

    def _change_item_amount(
        self, category: Category, item: str, amount: float
    ) -> None:
        if category == Category.ASSETS:
            item_val = self.assets.get_item_val(item)
            self.assets.update_item_value(item, item_val - amount)
        else:
            item_val = self.liabilities.get_item_val(item)
            self.liabilities.update_item_value(item, item_val - amount)
