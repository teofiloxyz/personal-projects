from tabulate import tabulate

import re
from typing import Optional
from enum import Enum

from fintracker import Fintracker
from database import Edit
from utils import Utils, Date

# Still needs a lot of work


class CategoryType(Enum):
    ASSETS = "Assets"
    LIABILITIES = "Liabilities"

    def singular(self) -> str:
        SINGULAR = {"Assets": "Asset", "Liabilities": "Liability"}
        return SINGULAR[self.value]


class BalanceCategory:
    def __init__(self) -> None:
        self.utils = Utils()
        self.category: dict[str, float]
        self.category_title: CategoryType
        self.total_category_title: str

    def get_items(self) -> dict[str, float]:
        return self.category

    def get_items_as_currency(self) -> list[tuple]:
        category = [
            (item.capitalize(), self.utils.get_val_as_currency(amount))
            for item, amount in self.category.items()
        ]
        category.append(
            (
                self.total_category_title,
                self.utils.get_val_as_currency(self.get_total_value()),
            )
        )
        return category

    def get_total_value(self) -> float:
        return sum(self.category.values())

    def print_items_with_index(
        self, index_start: int = 1, show_create_new: bool = True
    ) -> None:
        print(f"\n{self.category_title.value.capitalize()}:")
        [
            print(f"[{n}] {item.capitalize()}")
            for n, item in enumerate(self.category.keys(), index_start)
        ]
        if show_create_new:
            n = index_start + len(self.category)
            print(f"[{n}] Create a new {self.category_title.singular()}")

    def create_new_item(self) -> Optional[str]:
        while True:
            item = input(
                f"Enter name for the new {self.category_title.singular()}: "
            ).lower()
            if item == "q":
                return None
            elif item in self.category.keys():
                print(
                    f"Cannot create {self.category_title.singular()}: '{item}'"
                )
                continue
            self.category[item] = 0
            return item

    def change_item_val(self, item: str) -> Optional[float]:
        item_val = self.category[item]
        print(f"Current value of {item.capitalize()}: {item_val}")
        while True:
            item_new_val = input(
                f"Enter the new value for {item.capitalize()}: "
            )
            if item_new_val == "q":
                return
            try:
                item_new_val = float(item_new_val)
            except ValueError:
                print("Must be a number...")
                continue
            if item_new_val < 0:
                print("Cannot be negative!")
                continue
            return round(item_new_val - item_val, 2)


class Assets(BalanceCategory):
    def __init__(self) -> None:
        self.utils = Utils()
        self.category = Fintracker().assets
        self.category_title = CategoryType.ASSETS


class Liabilities(BalanceCategory):
    def __init__(self) -> None:
        self.utils = Utils()
        self.category = Fintracker().liabilities
        self.category_title = CategoryType.LIABILITIES


class Balance:
    fintracker, assets, liabilities = Fintracker(), Assets(), Liabilities()
    utils, date = Utils(), Date()

    def show(self) -> None:
        assets = self.assets.get_items_as_currency()
        liabilities = self.liabilities.get_items_as_currency()
        balance = assets + liabilities

        assets_total_value = self.assets.get_total_value()
        liabilities_total_value = self.liabilities.get_total_value()
        balance_total_value = assets_total_value - liabilities_total_value
        balance.append(
            ("Balance", self.utils.get_val_as_currency(balance_total_value))
        )

        table = tabulate(
            balance,
            headers=("Item", "Amount"),
            tablefmt="fancy_grid",
            stralign="center",
        )
        print(table)

    def edit(self) -> None:
        category_item = self._pick_balance_item(
            question="Choose the item to edit: "
        )
        if not category_item:
            print("Aborting...")
            return
        category, item = category_item

        if category == CategoryType.ASSETS:
            val_diff = self.assets.change_item_val(item)
            item_val = self.assets.category[item]
            del self.assets.category[item]
        else:
            val_diff = self.liabilities.change_item_val(item)
            item_val = self.liabilities.category[item]
            del self.liabilities.category[item]
        if not val_diff:
            print("Aborting...")
            return

        ast_operation, lib_operation = self._get_val_operations(
            category.value, val_diff
        )

        """ Show again all balance items except the chosen """
        category_item_2 = self._pick_balance_item(
            question=f"Choose an asset to {ast_operation} or liability "
            f"to {lib_operation}, or leave empty if is isolated: ",
            can_cancel=True,
        )
        if not category_item_2:
            print("Aborting...")
            return
        category_2, item_2 = category_item_2
        if category_2 == CategoryType.ASSETS:
            item_2_val = self.assets.category[item_2]
        else:
            item_2_val = self.liabilities.category[item_2]
        item_2_new_val = self._get_item_2_new_val(
            category, category_2, item_2_val, val_diff
        )

        if category_2 == CategoryType.ASSETS:
            self.assets.category[item_2] = item_2_new_val
        else:
            self.liabilities.category[item_2] = item_2_new_val

        description = self._create_operation_description(
            category.value, item, category_2.value, item_2, val_diff
        )
        # reinsert first item and update item2 val
        if category == CategoryType.ASSETS:
            self.assets.category[item] = item_val + val_diff
        else:
            self.liabilities.category[item] = item_val + val_diff

        now = self.date.get_now(date_format="%Y-%m-%d %H:%M:%S")
        entry = now, "Balance", abs(val_diff), description
        Edit().add_transaction(entry)
        # improve save
        self.fintracker.save()
        self.check_for_balance_negative_items()

    def _pick_item(
        self, question: str, can_cancel: bool = False
    ) -> Optional[tuple]:
        while True:
            self.assets.print_items_with_index()
            assets = [
                (CategoryType.ASSETS, item)
                for item in self.assets.get_items().keys()
            ]
            assets += [(CategoryType.ASSETS, "create new")]

            self.liabilities.print_items_with_index(index_start=len(assets) + 1)
            liabilities = [
                (CategoryType.LIABILITIES, item)
                for item in self.liabilities.get_items().keys()
            ]
            liabilities += [(CategoryType.LIABILITIES, "create new")]
            balance = assets + liabilities

            prompt = input(f"\n{question}")
            if prompt == "" and can_cancel or prompt == "q":
                return None
            elif not prompt.isdigit() or not (1 <= int(prompt) <= len(balance)):
                print("Pick a number within those...")
                continue

            category, item = balance[int(prompt) - 1]
            if item == "create new":
                if category == CategoryType.ASSETS:
                    item = self.assets.create_new_item()
                else:
                    item = self.liabilities.create_new_item()
            return category, item

    def _get_val_operations(
        self, category: str, val_diff: float
    ) -> tuple[str, str]:
        val_diff_abs = self.utils.get_val_as_currency(abs(val_diff))

        if (val_diff > 0 and category == "assets") or (
            val_diff < 0 and category != "assets"
        ):
            return f"subtract {val_diff_abs}", f"add {val_diff_abs}"
        else:
            return f"add {val_diff_abs}", f"subtract {val_diff_abs}"

    def _get_item_2_new_val(
        self, category: str, category_2: str, item_2_val: float, val_diff: float
    ) -> float:
        if category == category_2:
            return item_2_val - val_diff
        else:
            return item_2_val + val_diff

    def _create_operation_description(
        self,
        category: str,
        item: str,
        category_2: str,
        item_2: str,
        val_diff: float,
    ) -> str:
        item_1_opr = "-" if val_diff < 0 else "+"
        description = f"{item_1_opr}{category[0]}:{item}"
        if category == category_2:
            item_2_opr = "+" if val_diff < 0 else "-"
        else:
            item_2_opr = "-" if val_diff < 0 else "+"

        if category_2 != "":  # In case of isolated
            description += f" {item_2_opr}{category_2[0]}:{item_2}"
        return description

    def check_for_negative_items(self) -> None:
        balance_negative_items = self.get_balance_negative_items()
        if len(balance_negative_items) > 0:
            self.show_balance_negative_items(balance_negative_items)

    def get_negative_items(self) -> list[str]:
        return [
            item
            for category in self.fintracker.balance.values()
            for item, amount in category.items()
            if amount < 0
        ]

    def change_cash_amount(self, amount: float) -> None:
        self.fintracker.balance["assets"]["cash"] += amount

    def change_item_amount(self, entry: tuple) -> None:
        # item_1 = re.sub(" [-+][la]:.*$", "", note)
        # self.balance.change_item_amount(item_1)
        # item_2 = note.replace(item_1, "").strip()
        ## if not isolated balance transaction, change to be reversed
        # if item_2 != "":
        #    self.balance.change_item_amount(item_2)
        category = "assets" if entry[1] == "a" else "liabilities"
        item = entry[3:]
        operation = entry[0]

        item_val = (
            self.fintracker.balance[category][item]
            if item in self.fintracker.balance[category].keys()
            else 0
        )
        if operation == "+":
            # Reversed bc removed transaction
            self.fintracker.balance[category][item] = item_val - amount
        else:
            self.fintracker.balance[category][item] = item_val + amount

    def __exit__(self) -> None:
        # self.fintracker.save()
        self.check_for_negative_items()
