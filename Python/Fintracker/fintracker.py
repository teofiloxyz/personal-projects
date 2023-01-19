from utils import Utils


class Fintracker:
    def __init__(self) -> None:
        self.auto_transactions: dict = Utils().load_json(
            "auto_transactions.json"
        )
        self.balance: dict = Utils().load_json("balance.json")
        self.assets, self.liabilities = self.balance.values()

    def save(self) -> None:
        Utils().write_json("auto_transactions.json", self.auto_transactions)
        Utils().write_json("balance.json", self.balance)
