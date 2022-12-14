#!/usr/bin/python3


class Balance:
    def show_balance(self):
        assets = self.json_info["assets"]
        assets_sum = sum(assets.values())
        liabilities = self.json_info["liabilities"]
        liabilities_sum = sum(liabilities.values())
        balance = assets_sum - liabilities_sum

        print(
            f"{ffmt.bold}{fcol.green}Assets:{ffmt.reset} "
            f"{'€ {:,.2f}'.format(assets_sum)}"
        )
        [
            print(f"{asset.capitalize()}: {'€ {:,.2f}'.format(amount)}")
            for asset, amount in assets.items()
        ]

        print(
            f"\n{ffmt.bold}{fcol.red}Liabilities:{ffmt.reset} "
            f"{'€ {:,.2f}'.format(liabilities_sum)}"
        )
        [
            print(f"{liability.capitalize()}: {'€ {:,.2f}'.format(amount)}")
            for liability, amount in liabilities.items()
        ]

        print(
            f"\n{ffmt.bold}{fcol.yellow}Balance:{ffmt.reset} "
            f"{'€ {:,.2f}'.format(balance)}"
        )

    def edit_balance(self):
        def pick_balance_item(question, can_cancel=False):
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
                    return
                elif selection == "" and can_cancel:
                    return None, None
                try:
                    selection = int(selection)
                except ValueError:
                    print("Pick a number...")
                    continue

                if 0 < selection <= len(items_list):
                    # len assets + 1 por causa do create new
                    if selection <= len(balance["assets"]) + 1:
                        category = "assets"
                    else:
                        category = "liabilities"

                    item = items_list[selection - 1]

                    if item == "create new":
                        while True:
                            singular = (
                                "asset" if category == "assets" else "liability"
                            )
                            item = input(
                                "Enter name for the new " f"{singular}: "
                            ).lower()
                            if item == "q":
                                print("Aborting...")
                                return
                            elif item in self.json_info[category].keys():
                                if category == "assets":
                                    print(
                                        "There's already an asset named "
                                        f"{item}"
                                    )
                                else:
                                    print(
                                        "There's already a liability "
                                        f"named {item}"
                                    )
                                continue
                            break
                        balance[category][item] = 0

                    return (category, item)

        # dict para fazer uma cópia
        balance = {
            "assets": dict(self.json_info["assets"]),
            "liabilities": dict(self.json_info["liabilities"]),
        }

        try:
            category, item = pick_balance_item("Choose the item to edit: ")
        except TypeError:
            return

        item_val = balance[category][item]
        print(f"Current value of {item.capitalize()}: {item_val}")

        while True:
            new_item_val = input(
                "Enter the new value for " f"{item.capitalize()}: "
            )
            if new_item_val == "q":
                print("Aborting...")
                return
            try:
                new_item_val = float(new_item_val)
            except ValueError:
                print("Must be a number...")
                continue
            if new_item_val < 0:
                print("Cannot be negative!")
                continue
            break

        del balance[category][item]

        val_diff = round(new_item_val - item_val, 2)
        if (val_diff > 0 and category == "assets") or (
            val_diff < 0 and category != "assets"
        ):
            ast_operation, lib_operation = "subtract", "add"
        else:
            ast_operation, lib_operation = "add", "subtract"

        description = "-" if val_diff < 0 else "+"
        description += f"{category[0]}:{item}"

        val_diff = abs(val_diff)
        ast_operation += f" € {val_diff}"
        lib_operation += f" € {val_diff}"

        while True:
            try:
                category_2, item_2 = pick_balance_item(
                    f"Choose an asset to {ast_operation} or "
                    f"liability to {lib_operation}, or "
                    "leave empty if is isolated: ",
                    can_cancel=True,
                )
            except TypeError:
                return

            if category_2 is None:
                break

            item_2_val = balance[category_2][item_2]
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

            if new_item_2_val < 0:
                print(
                    f"{item_2.capitalize()} can't become negative..."
                    "\nChoose another item, or cancel by entering [q]"
                )
                continue
            break

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = now, "Balance", val_diff, description
        self.cursor.execute(
            "INSERT INTO transactions (time, "
            f"trn_type, amount, note) VALUES {entry}"
        )
        self.db_con.commit()

        self.json_info[category][item] = new_item_val
        if category_2 is not None:
            self.json_info[category_2][item_2] = new_item_2_val
        self.save_json()
