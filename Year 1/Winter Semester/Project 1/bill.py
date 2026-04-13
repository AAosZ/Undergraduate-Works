from typing import Union


class Bill:
    billed_min: int
    free_min: int
    min_rate: float
    fixed_cost: float
    type: str

    def __init__(self) -> None:
        self.billed_min = 0
        self.free_min = 0
        self.fixed_cost = 0
        self.min_rate = 0
        self.type = ""

    def set_rates(self, contract_type: str, min_cost: float) \
            -> None:
        self.type = contract_type
        self.min_rate = min_cost

    def add_fixed_cost(self, cost: float) -> None:
        self.fixed_cost += cost

    def add_billed_minutes(self, minutes: int) -> None:
        self.billed_min += minutes

    def add_free_minutes(self, minutes: int) -> None:
        self.free_min += minutes

    def get_cost(self) -> float:
        return self.min_rate * self.billed_min + self.fixed_cost


    def get_summary(self) -> dict[str, Union[float, int]]:

        bill_summary = {'type': self.type,
                        'fixed': self.fixed_cost,
                        'free_mins': self.free_min,
                        'billed_mins': self.billed_min,
                        'min_rate': self.min_rate,
                        'total': self.get_cost()
                        }
        return bill_summary


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing'
        ],
        'disable': ['R0902'],
        'generated-members': 'pygame.*'
    })
