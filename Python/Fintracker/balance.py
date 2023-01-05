from Tfuncs import fcol, ffmt
from tabulate import tabulate

from utils import Utils, Fintracker
from transactions import Transactions


class Balance:
    utils = Utils()
    transactions = Transactions()

    def show(self) -> None:
        assets, liabilities = Fintracker.balance.values()
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

    def edit(self) -> None:
        assets, liabilities = Fintracker.balance.values()

        balance = {
            "assets": dict(assets),  # dict para fazer uma cópia
            "liabilities": dict(liabilities),
        }

        category, item = self.pick_balance_item(
            "Choose the item to edit: ", balance
        )
        if category is None:
            return

        if item == "create new":
            item = self.create_new_item(category)
            if item is None:
                return
            balance[category][item] = 0

        item_val = balance[category][item]
        item_new_val = self.get_item_new_val(item, item_val)
        if item_new_val is None:
            return
        del balance[category][item]

        val_diff = self.get_val_diff(item_val, item_new_val)
        ast_operation, lib_operation = self.get_val_operations(
            category, val_diff
        )
        description = self.create_operation_description(
            category, item, val_diff
        )

        while True:
            category_2, item_2 = self.pick_balance_item(
                f"Choose an asset to {ast_operation} or liability "
                f"to {lib_operation}, or leave empty if is isolated: ",
                balance,
                can_cancel=True,
            )
            if category_2 is None:
                break
            if item_2 == "create new":
                item_2 = self.create_new_item(category)
                if item_2 is None:
                    break
                balance[category][item] = 0
            item_2_val = balance[category_2][item_2]

            new_item_2_val, description = self.get_item_2_val_and_description(
                category_2,
                item_2,
                item_2_val,
                val_diff,
                ast_operation,
                lib_operation,
                description,
            )

            if new_item_2_val < 0:
                print(
                    f"{item_2.capitalize()} can't become negative..."
                    "\nChoose another item, or cancel by entering [q]"
                )
                continue
            break

        now = self.utils.get_date_now()
        entry = now, "Balance", val_diff, description
        self.transactions.add(entry)

        self.save_balance_info(category, item, new_item_val)
        if category_2 is not None:
            self.save_balance_info(category_2, item_2, new_item_2_val)

    def get_category_as_currency(self, category: dict) -> list[tuple]:
        return [
            (item.capitalize(), self.utils.get_val_as_currency(amount))
            for item, amount in category.items()
        ]

    def pick_balance_item(
        self, question: str, balance: dict, can_cancel: bool = False
    ) -> tuple[str | None, str | None]:
        # needs simplification
        while True:
            items_list, n = list(), 1
            for items in balance.items():
                print(f"\n{items[0].capitalize()}: ")
                for item in items[1]:
                    print(f"[{n}] {item.capitalize()}")
                    items_list.append(item)
                    n += 1
                singular = "asset" if items[0] == "assets" else "liability"
                print(f"[{n}] Create new {singular}")
                items_list.append("create new")
                n += 1

            selection = input(f"\n{question}")
            if selection == "q":
                print("Aborting...")
                return None, None
            elif selection == "" and can_cancel:
                return None, None
            try:
                selection = items_list[int(selection)]
            except (ValueError, IndexError):
                print("Pick a number within those...")
                continue

            # need total rework
            if 0 < selection <= len(items_list):
                # len assets + 1 por causa do create new
                if selection <= len(balance["assets"]) + 1:
                    category = "assets"
                else:
                    category = "liabilities"
                item = items_list[selection - 1]
                return (category, item)

    def create_new_item(self, category: str) -> str | None:
        while True:
            singular_cat = "asset" if category == "assets" else "liability"
            item = input(f"Enter name for the new {singular_cat}: ").lower()
            if item == "q":
                print("Aborting...")
                return None
            if self.check_if_item_exists(category, item):
                continue
            break

    def get_item_new_val(self, item: str, item_val: float) -> float | None:
        print(f"Current value of {item.capitalize()}: {item_val}")
        while True:
            item_new_val = input(
                f"Enter the new value for {item.capitalize()}: "
            )
            if item_new_val == "q":
                print("Aborting...")
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

    def get_val_diff(self, item_val: float, item_new_val: float) -> float:
        return round(item_new_val - item_val, 2)

    def get_val_operations(
        self, category: str, val_diff: float
    ) -> tuple[str, str]:
        val_diff_abs = str(abs(val_diff))
        if (val_diff > 0 and category == "assets") or (
            val_diff < 0 and category != "assets"
        ):
            return f"subtract € {val_diff_abs}", f"add € {val_diff_abs}"
        else:
            return f"add € {val_diff_abs}", f"subtract € {val_diff_abs}"

    def create_operation_description(
        self, category: str, item: str, val_diff: float
    ) -> str:
        description = "-" if val_diff < 0 else "+"
        description += f"{category[0]}:{item}"
        return description

    def get_item_2_val_and_description(
        self,
        category_2: str,
        item_2: str,
        item_2_val: float,
        val_diff: float,
        ast_operation: str,
        lib_operation: str,
        description: str,
    ) -> tuple[float, str]:
        # rework func, too many args ...
        if category_2 == "assets":
            if ast_operation.startswith("subtract"):
                new_item_2_val = item_2_val - val_diff
                description += f" -a:{item_2}"
            else:
                new_item_2_val = item_2_val + val_diff
                description += f" +a:{item_2}"
        else:
            if lib_operation.startswith("subtract"):
                new_item_2_val = item_2_val - val_diff
                description += f" -l:{item_2}"
            else:
                new_item_2_val = item_2_val + val_diff
                description += f" +l:{item_2}"

        return new_item_2_val, description

    def save_balance_info(
        self, category: str, item: str, new_item_val: float
    ) -> None:
        # rework
        json_info = self.utils.load_json()
        json_info[category][item] = new_item_val
        self.utils.write_json(json_info)

    def check_if_item_exists(self, category: str, item: str) -> bool:
        json_info = self.utils.load_json()
        if item in json_info[category].keys():
            if category == "assets":
                print(f"There's already an asset named {item}")
            else:
                print(f"There's already a liability named {item}")
            return True
        return False
