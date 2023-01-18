from Tfuncs import fcol, ffmt
from tabulate import tabulate

from fintracker import Fintracker
from utils import Utils, Date
from transactions import Transactions


class Balance:
    fintracker = Fintracker()
    utils, date = Utils(), Date()
    transactions = Transactions()

    def show(self) -> None:
        assets, liabilities = self.fintracker.balance.values()
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())

        assets = self.get_category_as_currency(assets)
        assets.append(
            (
                f"{ffmt.bold}{fcol.green}Total Assets",
                self.utils.get_val_as_currency(total_assets) + ffmt.reset,
            )
        )
        liabilities = self.get_category_as_currency(liabilities)
        liabilities.append(
            (
                f"{ffmt.bold}{fcol.red}Total Liabilities",
                self.utils.get_val_as_currency(total_liabilities) + ffmt.reset,
            )
        )
        balance = assets + liabilities
        balance.append(
            (
                f"{ffmt.bold}Balance",
                self.utils.get_val_as_currency(total_assets - total_liabilities)
                + ffmt.reset,
            )
        )

        table = tabulate(
            balance,
            headers=(f"{ffmt.bold}{fcol.cyan}Item", f"Amount{ffmt.reset}"),
            tablefmt="fancy_grid",
            stralign="center",
        )
        print(table)

    def get_category_as_currency(self, category: dict) -> list[tuple]:
        return [
            (item.capitalize(), self.utils.get_val_as_currency(amount))
            for item, amount in category.items()
        ]

    def edit(self) -> None:
        # made a copy here
        balance = self.fintracker.balance
        category, item = self.pick_balance_item(
            balance, question="Choose the item to edit: "
        )
        if category == "q":
            print("Aborting...")
            return

        if item == "create new":
            item = self.create_new_item(category)
            if item == "":
                print("Aborting...")
                return
            balance[category][item] = 0

        item_val = balance[category][item]
        item_new_val = self.get_item_new_val(item, item_val)
        if item_new_val is None:
            print("Aborting...")
            return
        val_diff = round(item_new_val - item_val, 2)
        ast_operation, lib_operation = self.get_val_operations(
            category, val_diff
        )

        """ Show again all balance items except the chosen """
        del balance[category][item]
        category_2, item_2 = self.pick_balance_item(
            balance,
            question=f"Choose an asset to {ast_operation} or liability "
            f"to {lib_operation}, or leave empty if is isolated: ",
            can_cancel=True,
        )
        if category_2 == "q":
            print("Aborting...")
            return

        """ If item not isolated """
        if category_2 != "":
            if item_2 == "create new":
                item_2 = self.create_new_item(category_2)
                if item_2 == "":
                    print("Aborting...")
                    return
                balance[category_2][item_2] = 0

            item_2_val = balance[category_2][item_2]
            item_2_new_val = self.get_item_2_new_val(
                category, category_2, item_2_val, val_diff
            )

        description = self.create_operation_description(
            category, item, category_2, item_2, val_diff
        )

        now = self.date.get_date_now(date_format="%Y-%m-%d %H:%M:%S")
        entry = now, "Balance", abs(val_diff), description
        self.transactions.add_entry(entry)

        self.fintracker.balance[category][item] = item_new_val
        if category_2 != "":
            self.fintracker.balance[category_2][item_2] = item_2_new_val
        self.fintracker.save()
        self.transactions.check_for_balance_negative_items()

    def pick_balance_item(
        self, balance: dict, question: str, can_cancel: bool = False
    ) -> tuple:
        while True:
            items, n = list(), 1
            print("\nAssets:")
            print(f"[{n}] Create new asset")
            items.append(("assets", "create new"))
            for n, asset in enumerate(balance["assets"].keys(), n + 1):
                print(f"[{n}] {asset.capitalize()}")
                items.append(("assets", asset))

            print("\nLiabilities:")
            print(f"[{n + 1}] Create new liability")
            items.append(("liabilities", "create new"))
            for n, liability in enumerate(balance["liabilities"].keys(), n + 2):
                print(f"[{n}] {liability.capitalize()}")
                items.append(("liabilities", liability))

            prompt = input(f"\n{question}")
            if prompt == "" and can_cancel or prompt == "q":
                return prompt, prompt
            try:
                return items[int(prompt) - 1]
            except (ValueError, IndexError):
                print("Pick a number within those...")
                continue

    def create_new_item(self, category: str) -> str:
        while True:
            category_sing = "asset" if category == "assets" else "liability"
            item = input(f"Enter name for the new {category_sing}: ").lower()
            if item == "q":
                return ""
            elif (
                item in self.fintracker.balance[category]
                or item == "create new"
            ):
                print(f"Cannot create {category_sing}: '{item}'")
                continue
            return item

    def get_item_new_val(self, item: str, item_val: float) -> float | None:
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
            return item_new_val

    def get_val_operations(
        self, category: str, val_diff: float
    ) -> tuple[str, str]:
        val_diff_abs = self.utils.get_val_as_currency(abs(val_diff))
        if (val_diff > 0 and category == "assets") or (
            val_diff < 0 and category != "assets"
        ):
            return f"subtract {val_diff_abs}", f"add {val_diff_abs}"
        else:
            return f"add {val_diff_abs}", f"subtract {val_diff_abs}"

    def get_item_2_new_val(
        self, category: str, category_2: str, item_2_val: float, val_diff: float
    ) -> float:
        if category == category_2:
            return item_2_val - val_diff
        else:
            return item_2_val + val_diff

    def create_operation_description(
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
